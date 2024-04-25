from socket import *
import os
from lib.message import *
from lib.constants import TIMEOUT, MAX_SYN_TRIES, MAX_FIN_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name):
        self.srv_address = str(srv_address)
        self.srv_port = int(srv_port)
        self.src_path = src_path
        self.file_name = file_name
        self.connected = False
        self.socket = None

    def connect(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT)

        syn_tries = 0
        while syn_tries < MAX_SYN_TRIES:
            try:
                self.socket.sendto(Message.new_syn().encode(), (self.srv_address, self.srv_port))
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)
                
                break
            except timeout:
                print("Timeout waiting for server ACK response. Retrying...")
                syn_tries += 1

        if syn_tries == MAX_SYN_TRIES:
            self.socket.close()
            self.socket = None
            print("Maximum SYN tries reached.")
            raise KeyboardInterrupt

        if decoded_msg.is_ack():
            self.socket.sendto(Message.new_syn_ok().encode(), (self.srv_address, self.srv_port))
            print("Connected to server.")
            self.connected = True

    def disconnect(self):
        fin_tries = 0
        while fin_tries < MAX_FIN_TRIES:
            try:
                self.socket.sendto(Message.new_end().encode(), (self.srv_address, self.srv_port))
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)

                break
            except Exception as e:
                print(f"Timeout waiting for server ACK response. Retrying...")
                fin_tries += 1

        if fin_tries == MAX_FIN_TRIES:
            print("Maximum FIN tries reached.")
            return

        if decoded_msg.is_ack():
            self.socket.sendto(Message.new_end_ok().encode(), (self.srv_address, self.srv_port))
            self.socket.close()
            self.connected = False
            print("Disconnected from server.")

    def upload(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.src_path)

        with open(file_path, "r") as file:
            file_size = os.path.getsize(file_path)
            file_name = self.file_name
            seq_num = 0

            for data in read_file_data(file, len(file_name)):
                data_size = len(data)
                tries = 0

                while tries < 3:
                    type = DATA_TYPE
                    if file_name != "":
                        type = PATH_TYPE
                    self.socket.sendto(Message(type, seq_num, data, file_name).encode(), (self.srv_address, self.srv_port))

                    try:
                        encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                        decoded_msg = Message.decode(encoded_msg)
                        if not decoded_msg.is_ack():
                            tries += 1
                            continue
                    except timeout:
                        tries += 1
                        print("Timeout waiting for server ACK response. Retrying...")
                        continue

                    file_name = ""
                    break

                if tries >= 3:
                    print(f"Failed to upload file.")
                    return
                
                if file_size - data_size <= 0:
                    print("File upload completed successfully.")

                seq_num += 1
                file_size -= data_size


def read_file_data(file, path_size):
    if path_size > MAX_MESSAGE_SIZE - 5:
        print(f"Destination file path length exceeds maximum value of: {MAX_MESSAGE_SIZE-5}")
        raise

    while True:
        if path_size == 0:
            data = file.read(MAX_MESSAGE_SIZE - 5)
        else:
            data = file.read(MAX_MESSAGE_SIZE - 2 - path_size - 5)
            
        if not data:
            break
        yield data
