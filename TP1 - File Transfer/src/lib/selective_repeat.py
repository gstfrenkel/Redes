from socket import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import * 
import time
import os

WINDOW_SIZE = 3
TIMEOUT_TYPE = -1

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
        self.pendings_len = 0

        self.requests = Queue()

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
                if self.base + WINDOW_SIZE >= self.seq_num:
                    with self.pendings_lock:
                        self.process_request()
                    continue

                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE

                message = Message(type, self.seq_num, data).encode()

                self.socket.sendto(message, self.address)

                with self.pendings_lock:
                    self.pendings[self.seq_num] = (message, time.time(), 0, False)
                    self.seq_num += 1
                file_size -= data_size






        if not empty_file:
            thread_recv_acks.join()
            thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message.new_ack().encode(), self.address)

        return not self.abort, self.seq_num
    
    def process_request(self):
        (type, seq_num) = self.requests.get()

        if type == TIMEOUT_TYPE:
            if seq_num not in self.pendings:
                return
            self.socket.sendto(self.pendings[seq_num], self.address)
            self.pendings[seq_num] = (self.pendings[0], )




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

            self.requests.put((ACK_TYPE, message.seq_num))
        
    def check_timeouts(self):
        while not self.abort and not self.disconnected:
            with self.pendings_lock:
                for k, v in self.pendings.items():
                    if time.time() - v[1] >= TIMEOUT:
                        self.requests.put((TIMEOUT_TYPE, k))







    def update_base_seq_num(self, message):
        if self.base != message.seq_num:
            return
        
        #print(f"\nEntró a update base con seq_num {message.seq_num}")

        if len(self.pendings) == 1:
            #print(f"Avanzó a {self.base + 1}")
            self.base += 1
            return
        
        next_base = -1
        for k, v in self.pendings.items():
            print(f"Pending: {k}: ({v[1]}, {v[3]})")
            if (next_base == -1 or k < next_base) and not v[3]:
                next_base = k

        if next_base == -1:
            next_base = self.seq_num #message.seq_num + WINDOW_SIZE

        #print(f"Avanzó a {next_base}")
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
            # Deberiamos mandar el ack del last data type y del disconnect
            
            if message.seq_num > self.seq_num + 1:      # Si llega un data posterior al que se necesita.
                self.pendings[message.seq_num] = message.data
                continue
            if message.seq_num != self.seq_num + 1:     # Si es un data repetido.
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
