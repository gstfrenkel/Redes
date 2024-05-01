from socket import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
from threading import * 
import time
import os

WINDOW_SIZE = 4

class SelectiveRepeat:
    def __init__(self, socket, address, file, seq_num):
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0
        self.seq_num = seq_num
        self.base_seq_num = seq_num

        self.pendings_lock = Lock()
        self.pendings = {}  # Set de ACKs (seqnum) con (Data, timestamp, tries)
        self.abort = False
        self.disconnected = False
    
    # Sender
    def send(self, file_path):
        thread_recv_acks = Thread(target=self.recv_acks, args=())
        thread_check_timeouts = Thread(target=self.check_timeouts, args=())
        thread_recv_acks.start()
        thread_check_timeouts.start()

        file_size = os.path.getsize(file_path)

        for data in read_file_data(self.file):
            data_size = len(data)
            print(f"Primer seq_num sin ACK: {self.base_seq_num}")            
            print(f"Seq_num a mandar: {self.seq_num}")
            
            while self.base_seq_num + WINDOW_SIZE < self.seq_num:
                if self.abort or self.disconnected:
                    break
                continue
            if self.abort or self.disconnected:
                break
            
            type = DATA_TYPE
            if file_size - data_size <= 0:
                type = LAST_DATA_TYPE

            message = Message(type, self.seq_num, data).encode()
            print(f"Manda el mensaje con data {self.seq_num}")
            self.socket.sendto(message, self.address)

            with self.pendings_lock:
                self.pendings[self.seq_num] = (message, time.time(), 0)
            self.seq_num += 1
            file_size -= data_size

        thread_recv_acks.join()
        thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message.new_ack().encode(), self.address)

        return not self.abort, self.seq_num

    def recv_acks(self):
        while not self.abort and not self.disconnected:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                print(f"Timeout waiting for ACK package {self.seq_num + 1}. Retrying...")
                continue
            message = Message.decode(enc_msg)
            with self.pendings_lock:
                if message.is_ack() and message.seq_num in self.pendings:
                    del self.pendings[message.seq_num]                  # Chequear de bloquear el thread entre el borrado y el editado del mensaje pendiente
                    self.update_base_seq_num(message)
                elif message.is_disconnect():
                    self.disconnected = True
        return
        
    def check_timeouts(self):
        while not self.abort and not self.disconnected:
            with self.pendings_lock:
                for key, val in self.pendings.items():
                    if time.time() - val[1] >= TIMEOUT:
                        print(f"Timeout en pkg {key}")
                        if val[2] >= MAX_TRIES:
                            self.abort = True
                            break
                        self.socket.sendto(val[0], self.address)
                        self.pendings[key] = (val[0], time.time(), val[2] + 1)  

    def update_base_seq_num(self, message):
        if self.base_seq_num != message.seq_num:
            return

        print("update on base_seq_num")

        min_seq_num = -1
        with self.pendings_lock:
            for key in self.pendings.keys():
                if min_seq_num == -1 or key < min_seq_num:
                    min_seq_num = key

        if min_seq_num == -1:
            min_seq_num = self.base_seq_num + WINDOW_SIZE

        print(f"NEW BASE SEQ NUM = {min_seq_num}")
        self.base_seq_num = min_seq_num














    # receiver
    def receive(self, is_server):
        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)
            print(f"Seq_num received: {message.seq_num}")
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
      
def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
