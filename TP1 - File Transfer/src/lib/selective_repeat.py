from socket import timeout
from lib.message import (
    Message, DATA_TYPE, ACK_TYPE, LAST_DATA_TYPE, END_TYPE, HEADER_SIZE)
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import Lock, Thread
import time
import os

WINDOW_SIZE = 7
TIMEOUT_TYPE = -1
DELETION_TIMESTAMP = -1


class SelectiveRepeat:
    def __init__(self, socket, address, file, seq_num, logger):
        self.logger = logger
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0

        self.seq_num = seq_num
        self.base = seq_num
        self.last_seq_num = None

        self.lock = Lock()

        self.pendings = {}  # ACKs (seqnum) con (Data, tries, acknowledged)

        self.requests = Queue()
        self.timestamps = Queue()

        self.abort = False
        self.disconnected = False

    # Sender
    def send(self, file_path, is_server):
        file_size = os.path.getsize(file_path)
        empty_file = file_size == 0

        if not empty_file:
            thread_recv_acks = Thread(target=self.recv_acks, args=())
            thread_check_timeouts = Thread(
                target=self.check_timeouts, args=())
            thread_recv_acks.start()
            thread_check_timeouts.start()

        for data in read_file_data(self.file):
            data_size = len(data)
            if self.disconnected:
                break

            while not self.abort and not self.disconnected:
                if self.base + WINDOW_SIZE <= self.seq_num:
                    self.process_request(is_server)
                    continue

                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE
                    self.last_seq_num = self.seq_num

                message = Message(type, self.seq_num, data).encode()
                if type == DATA_TYPE:
                    self.logger.print_msg(
                        f"Sent {self.seq_num} with window {self.base}")
                else:
                    self.logger.print_msg(
                        f"Sent last data {self.seq_num} " +
                        f"with window {self.base}")
                with self.lock:
                    self.socket.sendto(message, self.address)

                self.timestamps.put((self.seq_num, time.time()))

                self.pendings[self.seq_num] = (message, 0, False)
                self.seq_num += 1

                file_size -= data_size
                break

        while not self.abort and not self.disconnected:
            self.process_request(is_server)

        if not empty_file:
            thread_recv_acks.join()
            thread_check_timeouts.join()

        return not self.abort, self.seq_num

    def process_request(self, is_server):
        try:
            (type, seq_num, timestamp) = self.requests.get(False, TIMEOUT)
            pending = self.pendings[seq_num]
        except Exception:
            return

        if type == TIMEOUT_TYPE:
            if pending[2]:
                return
            if pending[1] + 1 >= MAX_TRIES:
                self.abort = True
                return

            with self.lock:
                self.socket.sendto(pending[0], self.address)
            self.logger.print_msg(
                f"Resent {seq_num} with window {self.base} " +
                f"and timestamp {timestamp}")

            self.timestamps.put((seq_num, time.time()))
            self.pendings[seq_num] = (pending[0], pending[1] + 1, pending[2])
        elif type == ACK_TYPE:
            if pending[2]:
                return
            self.pendings[seq_num] = (pending[0], 0, True)
            self.logger.print_msg(f"Received {seq_num}")
            if self.base != seq_num:
                return

            self.update_base_seq_num()

            for k, v in self.pendings.copy().items():
                if k < self.base and v[2]:
                    self.timestamps.put((k, DELETION_TIMESTAMP))
                    del self.pendings[k]

            if (not is_server and
                    self.last_seq_num and len(self.pendings) == 0):
                self.disconnected = True

    def update_base_seq_num(self):
        if len(self.pendings) == 1:
            self.base += 1

        next_base = -1
        for k, v in self.pendings.items():
            if (next_base == -1 or k < next_base) and not v[2]:
                next_base = k

        if next_base == -1:
            next_base = self.seq_num  # message.seq_num + WINDOW_SIZE

        self.base = next_base

    def recv_acks(self):
        while not self.abort and not self.disconnected:
            if self.tries >= MAX_TRIES:
                self.abort = True
                break

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.logger.print_msg(
                    "Timeout waiting for ACK package. Retrying...")
                self.tries += 1
                continue

            self.tries = 0
            message = Message.decode(enc_msg)

            if message.type == ACK_TYPE:
                self.requests.put((ACK_TYPE, message.seq_num, None))
            elif message.type == END_TYPE:
                with self.lock:
                    self.socket.sendto(
                        Message.new_ack().encode(), self.address)
                self.disconnected = True

    def check_timeouts(self):
        timestamps = {}

        while not self.abort and not self.disconnected:
            while True:
                try:
                    seq_num, timestamp = self.timestamps.get(False)

                    if timestamp != DELETION_TIMESTAMP:
                        timestamps[seq_num] = timestamp
                    else:
                        del timestamps[seq_num]
                except Exception:
                    break

            for k, v in list(timestamps.items()):
                if time.time() - v >= TIMEOUT:
                    self.requests.put((TIMEOUT_TYPE, k, v))
                    del timestamps[k]

    # receiver
    def receive(self, is_server, message):
        self.process_data(is_server, message)

        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.logger.print_msg(
                    "Timeout waiting for data package. Retrying...")
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)
            self.process_data(is_server, message)

        return self.tries < MAX_TRIES

    def process_data(self, is_server, message):
        self.logger.print_msg(
            f"Received {message.seq_num} while expecting {self.seq_num}")

        if message.is_disconnect() and is_server:
            self.socket.sendto(
                Message(ACK_TYPE, message.seq_num).encode(), self.address)
            self.abort = True
            return

        if is_server or not message.is_last_data_type():
            self.socket.sendto(
                Message.new_ack(message.seq_num).encode(), self.address)

        if message.seq_num > self.seq_num:
            self.pendings[message.seq_num] = message
            return
        if message.seq_num < self.seq_num:      # Si es un data repetido.
            return

        if message.seq_num == 0:  # Para que no escriba de más al principio
            self.seq_num += 1
            return

        self.file.write(message.data)
        self.abort = message.is_last_data_type() and not is_server
        self.seq_num += 1

        while self.seq_num in self.pendings:
            self.file.write(self.pendings[self.seq_num].data)
            self.abort = (
                self.pendings[self.seq_num].is_last_data_type() and
                not is_server)
            del self.pendings[self.seq_num]
            self.seq_num += 1


def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
