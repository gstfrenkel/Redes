from lib.message import Message
from lib.message import DATA_TYPE, LAST_DATA_TYPE, ACK_TYPE, HEADER_SIZE
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import Thread
import time
import os

WINDOW_SIZE = 3
TIMEOUT_TYPE = -1
DELETION_TIMESTAMP = -1

# Values for self.pendings set
DATA = 0
TRIES = 1
ACKNOWLEDGED = 2


class SelectiveRepeat:
    def __init__(self, a_socket, address, file, seq_num):
        self.socket = a_socket
        self.address = address
        self.file = file
        self.tries = 0

        self.seq_num = seq_num
        self.base = seq_num

        # Set de ACKs (seqnum) con (Data, tries, acknowledged)
        self.pendings = {}

        self.requests = Queue()
        self.timestamps = Queue()

        self.abort = False
        self.disconnected = False

    # Sender
    def send(self, file_path):
        file_size = os.path.getsize(file_path)
        empty_file = file_size == 0

        if not empty_file:
            thread_recv_acks = Thread(target=self.recv_acks, args=())
            thread_check_timeouts = Thread(target=self.check_timeouts, args=())
            thread_recv_acks.start()
            thread_check_timeouts.start()

        for data in read_file_data(self.file):
            data_size = len(data)

            while not self.abort and not self.disconnected:
                if self.base + WINDOW_SIZE <= self.seq_num:
                    self.process_request()
                    continue

                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE

                message = Message(type, self.seq_num, data).encode()

                self.socket.sendto(message, self.address)
                self.timestamps.put((self.seq_num, time.time()))

                self.pendings[self.seq_num] = (message, 0, False)
                self.seq_num += 1

                file_size -= data_size
                break

        if not empty_file:
            thread_recv_acks.join()
            thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message.new_ack().encode(), self.address)

        return not self.abort, self.seq_num

    def process_request(self):
        (type, seq_num) = self.requests.get()
        pending = self.pendings[seq_num]

        if type == TIMEOUT_TYPE:
            if not pending or pending[ACKNOWLEDGED]:
                return
            if pending[TRIES] + 1 >= MAX_TRIES:
                self.abort = True
                return
            self.socket.sendto(pending[DATA], self.address)
            print(f"Sent timeout {seq_num}")

            self.timestamps.put((seq_num, time.time()))

            data = pending[DATA]
            tries = pending[TRIES] + 1
            acnowledged = pending[ACKNOWLEDGED]

            self.pendings[seq_num] = (data, tries, acnowledged)

        elif type == ACK_TYPE:
            if pending[ACKNOWLEDGED]:
                return
            self.pendings[seq_num] = (pending[DATA], 0, True)
            if self.base != seq_num:
                return

            self.update_base_seq_num()
            for k in list(self.pendings.keys()):
                if k < self.base:
                    self.timestamps.put((k, DELETION_TIMESTAMP))
                    del self.pendings[k]

    def update_base_seq_num(self):
        if not self.pendings[self.base+1]:
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
            except TimeoutError:
                print("Timeout waiting for ACK package. Retrying...")
                self.tries += 1
                continue

            self.tries = 0
            message = Message.decode(enc_msg)

            if message.is_disconnect():
                self.disconnected = True
                break

            self.requests.put((ACK_TYPE, message.seq_num))

    def check_timeouts(self):
        timestamps = {}

        while not self.abort and not self.disconnected:
            try:
                seq_num, timestamp = self.timestamps.get(False)

                if timestamp != DELETION_TIMESTAMP:
                    timestamps[seq_num] = timestamp
                else:
                    del timestamps[seq_num]
            except Exception as _:
                _

            for k, v in list(timestamps.items()):
                if time.time() - v >= TIMEOUT:
                    self.requests.put((TIMEOUT_TYPE, k))
                    del timestamps[k]

    # receiver
    def receive(self, is_server):
        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except TimeoutError:
                print("Timeout")
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)

            print(f"Received {message.seq_num}")

            if is_server or not message.is_last_data_type():
                encoded_ack_msg = Message.new_ack(message.seq_num).encode()
                self.socket.sendto(encoded_ack_msg, self.address)
            # Deberiamos mandar el ack del last data type y del disconnect

            # Si llega un data posterior al que se necesita.
            if message.seq_num > self.seq_num + 1:
                self.pendings[message.seq_num] = message.data
                continue

            # Si es un data repetido.
            if message.seq_num != self.seq_num + 1:
                continue

            self.file.write(message.data)
            self.abort = message.is_last_data_type()
            self.seq_num += 1

            while self.seq_num in self.pendings:
                self.file.write(self.pendings[self.seq_num])
                self.abort = self.pendings[self.seq_num].is_last_data_type()
                self.seq_num += 1

        return self.tries < MAX_TRIES


def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
