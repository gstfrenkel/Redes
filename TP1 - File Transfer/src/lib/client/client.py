from socket import *
import os
from lib.stop_wait import *
from lib.message import *
from lib.constants import TIMEOUT, MAX_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name):
        srv_socket = socket(AF_INET, SOCK_DGRAM)
        srv_socket.settimeout(TIMEOUT)

        self.socket = srv_socket
        self.address = (srv_address, int(srv_port))
        self.src_path = src_path
        self.file_name = file_name
        self.tries = 0
        self.seq_num = 0

    def connect(self, message_type):
        while self.tries < MAX_TRIES:
            print(f"Attempting to establish connection with server...")
            self.socket.sendto(Message.new_connect(message_type, self.file_name).encode(), self.address)

            try:
                encoded_msg, address = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)
                self.seq_num += 1
                break
            except timeout:
                self.tries += 1
                continue

        if self.tries >= MAX_TRIES:
            print("Failed to establish connection with server.")
            return
        
        print("Successfully established connection with server.")
        self.tries = 0
        self.address = address
        return message


    def disconnect(self):
        while self.tries < MAX_TRIES:
            self.socket.sendto(Message.new_disconnect().encode(), self.address)

            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)

                if not message.is_ack():
                    self.tries += 1
                    continue

                break
            except timeout:
                self.tries += 1

        if self.tries >= MAX_TRIES:
            print("Failed to cleanly disconnect from server.")
        else:
            print("Successfully disconnected from server.")

        self.socket.close()

    def upload(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.src_path)

        with open(file_path, "r") as file:
            file_size = os.path.getsize(file_path)

            for data in read_file_data(file):
                data_size = len(data)

                while self.tries < MAX_TRIES:
                    type = DATA_TYPE
                    if file_size - data_size <= 0:
                        type = LAST_DATA_TYPE
                        
                    self.socket.sendto(Message(type, self.seq_num, data).encode(), self.address)

                    try:
                        encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                        message = Message.decode(encoded_msg)

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

        print("Successfully uploaded file.")


    def download(self, message):
        file = open(self.src_path, "wb+")
        file.write(message.data.encode())
        if message.is_last_data_type():
            return
        
        handler = StopAndWait(self.socket, self.address, file, self.seq_num)
        ok = handler.receive(False)
        if ok:
            print("Successfully downloaded file.")
        else:
            print(f"Failed to download file.")


        """while self.tries < MAX_TRIES:
            self.socket.sendto(Message(ACK_TYPE, self.seq_num).encode(), self.address)

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.tries += 1
                continue

            message = Message.decode(enc_msg)
            print(f"Received: {message.type} {message.seq_num}")
            print(f"{message.data}")

            if message.seq_num == self.seq_num + 1:
                self.tries = 0
                file.write(message.data.encode())
                self.seq_num = message.seq_num
            else:
                self.tries += 1
                
            if message.is_last_data_type():
                break


        if self.tries >= MAX_TRIES:
            print(f"Failed to download file.")
            return

        print("Successfully downloaded file.")"""


def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
