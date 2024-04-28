from socket import *
import os
from lib.message import *
from lib.constants import TIMEOUT, MAX_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name):
        srv_socket = socket(AF_INET, SOCK_DGRAM)
        srv_socket.settimeout(TIMEOUT)

        self.socket = srv_socket
        self.srv_address = str(srv_address)
        self.srv_port = int(srv_port)
        self.src_path = src_path
        self.file_name = file_name
        self.tries = 0
        self.seq_num = 0

    def connect(self, message_type):
        while self.tries < MAX_TRIES:
            print(f"Attempting to establish connection with server...")
            self.socket.sendto(Message.new_connect(message_type, self.file_name).encode(), (self.srv_address, self.srv_port))

            try:
                encoded_msg, address = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)
                self.seq_num += 1
                break
            except timeout:
                self.tries += 1
                continue

        if self.tries >= MAX_TRIES or not message.is_ack():
            print("Failed to establish connection with server.")
            return
        
        self.tries = 0
        self.address = address

        print("Successfully established connection with server.")


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

                        if not message.is_ack() and message.seq_num != self.seq_num:
                            self.tries += 1
                            continue
                        self.tries = 0
                    except timeout:
                        self.tries += 1
                        print("Timeout waiting for server ACK response. Retrying...")
                        continue

                    break

                if self.tries >= MAX_TRIES:
                    print(f"Failed to upload file.")
                    return

                self.seq_num += 1
                file_size -= data_size


    """def download(self):
        tries = 0
        while tries < MAX_DOWNLOAD_TRIES:
            self.socket.sendto(Message(DOWNLOAD_TYPE, 0, "", self.file_name).encode(), (self.srv_address, self.srv_port))

            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)
                if not decoded_msg.is_download_type():
                    tries += 1
                    continue
            except timeout:
                tries += 1
                print("Timeout waiting for server ACK response. Retrying...")
                continue

            break
        
        if tries == MAX_DOWNLOAD_TRIES:
            print("Connection error: ACK or first DOWNLOAD not received")
            return

        file = open(self.src_path, "wb+")
        file_size = decoded_msg.file_size
        file.write(decoded_msg.data.encode())
        file_size -= len(decoded_msg.data)
        self.socket.sendto(Message(ACK_TYPE, decoded_msg.seq_num).encode(), self.transfer_address)
        while file_size > 0:
            encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            decoded_msg = Message.decode(encoded_msg)
            if decoded_msg.is_data_type():
                file.write(decoded_msg.data.encode())
                file_size -= len(decoded_msg.data)
                self.socket.sendto(Message(ACK_TYPE, decoded_msg.seq_num).encode(), self.transfer_address)
            else:
                break

        file.close()"""

def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
