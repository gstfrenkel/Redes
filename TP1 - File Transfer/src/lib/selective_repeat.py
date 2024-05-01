from socket import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import * 
import time
import os

WINDOW_SIZE = 3

class SelectiveRepeat:
    def __init__(self, socket, address, file, seq_num):
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0
        self.seq_num = seq_num
        self.base = seq_num
        self.pendings_lock = Lock()
        self.pendings = {}  # Set de ACKs (seqnum) con (Data, timestamp, tries, acknowledged)
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
            
            while self.seq_num >= self.base + WINDOW_SIZE:
                if self.abort or self.disconnected:
                    break
                continue
            if self.abort or self.disconnected:
                break
            
            type = DATA_TYPE
            if file_size - data_size <= 0:
                type = LAST_DATA_TYPE

            message = Message(type, self.seq_num, data).encode()

            self.socket.sendto(message, self.address)

            with self.pendings_lock:
                print(f"Sent {self.seq_num}. Window base: {self.base}. Remaining file size: {file_size - data_size}")

                self.pendings[self.seq_num] = (message, time.time(), 0, False)
            self.seq_num += 1
            file_size -= data_size

        if not empty_file:
            thread_recv_acks.join()
            thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message.new_ack().encode(), self.address)

        return not self.abort, self.seq_num

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
                break

            with self.pendings_lock:
                print(f"Received {message.seq_num} of type {message.type}")
                self.pendings[message.seq_num] = (enc_msg, time.time(), 0, True)

                self.update_base_seq_num(message)

                # ----------------------- Es una villereada pero sino, no anda ( ͡❛ ͜ʖ ͡❛) -----------------------
                keys_to_delete = []
                for k in self.pendings.keys():
                    if k < self.base:
                        keys_to_delete.append(k)

                for k in keys_to_delete:
                    del self.pendings[k]
        
    def check_timeouts(self):
        while not self.abort and not self.disconnected:
            with self.pendings_lock:
                for k, v in self.pendings.items():
                    if time.time() - v[1] >= TIMEOUT and not v[3]:
                        if v[2] >= MAX_TRIES:
                            self.abort = True
                            break
                        self.socket.sendto(v[0], self.address)
                        self.pendings[k] = (v[0], time.time(), v[2] + 1, False)

    def update_base_seq_num(self, message):
        if self.base != message.seq_num:
            return
        
        print(f"\n\nEntró a update base con seq_num {message.seq_num}")

        if len(self.pendings) == 1:
            print(f"Avanzó a {self.base + 1}")
            self.base += 1
            return
        
        next_base = -1
        for k, v in self.pendings.items():
            print(f"Pending: {k}: ({v[1]}, {v[3]})")
            if (next_base == -1 or k < next_base) and not v[3]:
                next_base = k

        if next_base == -1:
            next_base = message.seq_num + WINDOW_SIZE

        print(f"Avanzó a {next_base}")
        self.base = next_base
    
    # receiver
    def receive(self, is_server):
        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                print("Timeout")
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)

            print(f"Received {message.seq_num}")

            if is_server or not message.is_last_data_type():
                self.socket.sendto(Message.new_ack(message.seq_num).encode(), self.address)
            
            if message.seq_num > self.seq_num + 1:      # Si llega un data posterior al que se necesita.
                self.pendings[message.seq_num] = message.data
                continue
            if message.seq_num != self.seq_num + 1:     # Si es un data repetido.
                continue

            self.file.write(message.data.encode())
            self.abort = message.is_last_data_type()
            self.seq_num += 1

            while self.seq_num in self.pendings:
                self.file.write(self.pendings[self.seq_num].encode())
                self.abort = self.pendings[self.seq_num].is_last_data_type()
                self.seq_num += 1      
        
        return self.tries < MAX_TRIES
      
def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
