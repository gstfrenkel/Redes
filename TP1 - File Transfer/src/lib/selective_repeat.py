from socket import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import * 
import time
import os

WINDOW_SIZE = 1
TIMEOUT_TYPE = -1
DELETION_TIMESTAMP = -1

class SelectiveRepeat:
    def __init__(self, socket, address, file, seq_num):
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0

        self.seq_num = seq_num
        self.base = seq_num

        self.pendings = {}  # Set de ACKs (seqnum) con (Data, tries, acknowledged)

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
            if self.disconnected:
                break

            while not self.abort and not self.disconnected:
                if self.base + WINDOW_SIZE <= self.seq_num:     # Si la ventana está llena
                    self.process_request(False)
                    continue

                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE

                message = Message(type, self.seq_num, data).encode()
                if type == DATA_TYPE:
                    print(f"Sent {self.seq_num} with window {self.base}")
                else:
                    print(f"Sent last data {self.seq_num} with window {self.base}")
                self.socket.sendto(message, self.address)
                self.timestamps.put((self.seq_num, time.time()))

                self.pendings[self.seq_num] = (message, 0, False)
                self.seq_num += 1

                file_size -= data_size
                break

        while not self.abort and not self.disconnected:
            self.process_request(False)

        if not empty_file:
            thread_recv_acks.join()
            thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message.new_ack().encode(), self.address)

        return not self.abort, self.seq_num
    
    def process_request(self, with_timeout):
        try:
            (type, seq_num) = self.requests.get(with_timeout, TIMEOUT)
            pending = self.pendings[seq_num]
        except Exception as _:
            if with_timeout:
                self.disconnected = True
            return

        if type == TIMEOUT_TYPE:
            if pending[2]:
                return
            if pending[1] + 1 >= MAX_TRIES:
                self.abort = True
                return
            self.socket.sendto(pending[0], self.address)
            print(f"Resent {seq_num} with window {self.base}")

            self.timestamps.put((seq_num, time.time()))
            self.pendings[seq_num] = (pending[0], pending[1] + 1, pending[2])
        elif type == ACK_TYPE:
            if pending[2]:
                return
            self.pendings[seq_num] = (pending[0], 0, True)
            print(f"Received {seq_num}")
            if self.base != seq_num:
                return
            
            self.update_base_seq_num()

            for k in self.pendings.copy().keys():
                if k < self.base:
                    self.timestamps.put((k, DELETION_TIMESTAMP))
                    del self.pendings[k]

    def update_base_seq_num(self):
        if len(self.pendings) == 1:
            self.base += 1
        
        next_base = -1
        for k, v in self.pendings.items():
            if (next_base == -1 or k < next_base) and not v[2]:
                next_base = k

        if next_base == -1:
            next_base = self.seq_num #message.seq_num + WINDOW_SIZE

        self.base = next_base  

    def recv_acks(self):
        while not self.abort and not self.disconnected:
            if self.tries >= MAX_TRIES:
                self.abort = True
                break

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                print(f"Timeout waiting for ACK package. Retrying...")
                self.tries += 1
                continue

            self.tries = 0
            message = Message.decode(enc_msg)

            if message.is_disconnect():
                self.disconnected = True
            else:
                self.requests.put((ACK_TYPE, message.seq_num))
        
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
                except Exception as _:
                    break

            for k, v in list(timestamps.items()):
                if time.time() - v >= TIMEOUT:
                    self.requests.put((TIMEOUT_TYPE, k))
                    del timestamps[k]

    # receiver
    def receive(self, is_server, message):
        self.process_data(is_server, message)

        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                print("Timeout when receiving")
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)
            self.process_data(is_server, message)

        return self.tries < MAX_TRIES
    
    def process_data(self, is_server, message):
        print(f"Received {message.seq_num} while expecting {self.seq_num+1}")
        self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)

        if is_server or not message.is_last_data_type():
            self.socket.sendto(Message.new_ack(message.seq_num).encode(), self.address)
        
        if message.seq_num > self.seq_num + 1:      # Si llega un data posterior al que se necesita.
            self.pendings[message.seq_num] = message
            return
        if message.seq_num < self.seq_num + 1:      # Si es un data repetido.
            return

        self.file.write(message.data)
        self.abort = message.is_last_data_type()
        self.seq_num = message.seq_num

        while self.seq_num + 1 in self.pendings:
            self.file.write(self.pendings[self.seq_num + 1].data)
            self.abort = self.pendings[self.seq_num + 1].is_last_data_type()
            del self.pendings[self.seq_num + 1]
            self.seq_num += 1
        
      
def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
