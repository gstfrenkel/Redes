from socket import * 
from lib.stop_wait import * 
from lib.message import * 
from lib.constants import TIMEOUT, MAX_MESSAGE_SIZE, MAX_TRIES
import os

class ServerClient:
    def __init__(self, address):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        cli_socket.settimeout(TIMEOUT)

        self.socket = cli_socket
        self.address = address
        self.file = None
        self.tries = 0
        self.seq_num = 0

    def start(self, message):
        if message.is_upload_type():
            self.file = open(message.data, "wb+")
            self.download()
        elif message.is_download_type():
            self.file = open(message.data, "r")
            self.upload(message.data)

        self.disconnect()

    def download(self):
        handler = StopAndWait(self.socket, self.address, self.file, self.seq_num)
        ok = handler.receive(True)
        if ok:
            print(f"Successfully uploaded file from {self.address[0]}:{self.address[1]}.")
        else:
            print(f"Failed to upload file from {self.address[0]}:{self.address[1]}.")
                

    def upload(self, file_path):
        file_size = os.path.getsize(file_path)
        self.seq_num += 1

        for data in read_file_data(self.file):
            data_size = len(data)

            while self.tries < MAX_TRIES:
                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE

                self.socket.sendto(Message(type, self.seq_num, data).encode(), self.address)
                print(f"Sending {type} {self.seq_num}")
                print(data)

                try:
                    encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                    message = Message.decode(encoded_msg)

                    if message.is_disconnect():
                        self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)
                        break

                    if not message.is_ack() or message.seq_num != self.seq_num:
                        self.tries += 1
                        continue
                    self.tries = 0
                except timeout:
                    self.tries += 1
                    print(f"Timeout waiting for ACK response for package {self.seq_num}. Retrying...")
                    continue

                break

            if self.tries >= MAX_TRIES:
                print(f"Failed to upload file.")
                return

            self.seq_num += 1
            file_size -= data_size

        if self.seq_num > 1:
            return
        
        while self.tries < MAX_TRIES:
            self.socket.sendto(Message(LAST_DATA_TYPE, self.seq_num, "").encode(), self.address)
            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)

                if message.is_disconnect():
                    self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)
                    break
            except timeout:
                self.tries += 1

    def disconnect(self):
        if self.file:
            self.file.close()
        self.socket.close()
        print(f"Successfully disconnected from {self.address[0]}:{self.address[1]}.")
            

def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
