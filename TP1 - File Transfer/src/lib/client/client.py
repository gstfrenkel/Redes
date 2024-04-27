from socket import *
import os
from lib.message import *
from lib.constants import TIMEOUT, MAX_SYN_TRIES, MAX_FIN_TRIES, MAX_MESSAGE_SIZE, MAX_UPLOAD_TRIES, MAX_DOWNLOAD_TRIES

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name):
        self.srv_address = str(srv_address)
        self.srv_port = int(srv_port)
        self.src_path = src_path
        self.file_name = file_name
        self.connected = False
        self.socket = None
        self.transfer_address = None

    def connect(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT)

        syn_tries = 0
        while syn_tries < MAX_SYN_TRIES:
            try:
                self.socket.sendto(Message.new_syn().encode(), (self.srv_address, self.srv_port))
                encoded_msg, transfer_address = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)
                self.transfer_address = transfer_address
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

                while tries < MAX_UPLOAD_TRIES:
                    type = DATA_TYPE
                    address = self.transfer_address
                    if seq_num == 0:
                        type = UPLOAD_TYPE
                        address = (self.srv_address, self.srv_port)
                    print(f'mandando numero {seq_num} al address {address}')
                    self.socket.sendto(Message(type, seq_num, data, file_name, file_size).encode(), address)

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

                if tries >= MAX_UPLOAD_TRIES:
                    print(f"Failed to upload file.")
                    return

                if file_size - data_size <= 0:
                    end_tries = 0
                    while end_tries >= MAX_UPLOAD_TRIES:
                        self.socket.sendto(Message(type, seq_num, data, file_name, file_size).encode(), address)
                        try:
                            encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                            decoded_msg = Message.decode(encoded_msg)
                            if not decoded_msg.is_ack():
                                tries += 1
                                continue
                        except timeout:
                    print("File upload completed successfully.")

                seq_num += 1
                file_size -= data_size

    def download(self):
        tries = 0
        while tries < MAX_DOWNLOAD_TRIES:
            self.socket.sendto(Message(DOWNLOAD_TYPE, 0, "", self.file_name).encode(), (self.srv_address, self.srv_port))

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
        
        if tries == MAX_DOWNLOAD_TRIES:
            print("Connection error: ACK or first DOWNLOAD not received")
            return

        file = open(self.file_name, "wb+")

        # Recibir del server el archivo e ir recibiendo
        while True:
            encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            decoded_msg = Message.decode(encoded_msg)
            if decoded_msg.is_download_type():
                file.write(decoded_msg.data.encode())
                self.socket.sendto(Message(ACK_TYPE, decoded_msg.seq_num).encode(), (self.srv_address, self.srv_port))
            else:
                break

        file.close()

def read_file_data(file, path_size):
    max_path_size = MAX_MESSAGE_SIZE - 5
    if path_size > max_path_size:
        print(f"Destination file path length exceeds maximum value of: {max_path_size}")
        raise

    while True:
        if path_size == 0:
            data = file.read(max_path_size)
        else:
            # 2 is the sizeof(len(source_path)) and 32 is the sizeof(file_size)
            data = file.read(max_path_size - path_size - 2 - 32)

        if not data:
            break
        yield data
