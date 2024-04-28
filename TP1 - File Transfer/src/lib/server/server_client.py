from socket import * 
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
        self.is_client_downloading = False
        self.last_seq_num = 0

    def start(self, message):
        self.file = open(message.data, "wb+")

        if message.is_upload_type():
            self.upload()
        elif message.is_download_type():
            self.download()

        self.disconnect()

    def upload(self):
        while self.tries < MAX_TRIES:
            self.socket.sendto(Message(ACK_TYPE, self.last_seq_num).encode(), self.address)

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                print("Timeout waiting for more data")
                self.tries += 1
                continue

            message = Message.decode(enc_msg)

            if message.is_disconnect():
                self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)
                break

            if message.seq_num == self.last_seq_num + 1:
                self.tries = 0
                self.file.write(message.data.encode())
                self.last_seq_num = message.seq_num
            else:
                self.tries += 1
                

    def download(self):
        while True:
            message, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)




    def disconnect(self):
        if self.file:
            self.file.close()
        self.socket.close()
        print(f"Successfully disconnected from {self.address[0]}:{self.address[1]}.")
            

    def send_file_to_client(self, message, address):
        file_size = os.path.getsize(message.file_name)
        file_name = message.file_name

        with open(message.file_name, "r") as file:
            seq_num = 0

            for data in read_file_data(file, len(file_name)):
                data_size = len(data)
                tries = 0

                while tries < 3:
                    type = DATA_TYPE
                    if file_name != "":
                        type = DOWNLOAD_TYPE
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

                if tries >= 3:
                    print(f"Failed to upload file.")
                    return
                
                if file_size - data_size <= 0:
                    print("File download completed successfully.")

                seq_num += 1
                file_size -= data_size

def read_file_data(file, path_size):
    max_path_size = MAX_MESSAGE_SIZE - 5
    if path_size > max_path_size:
        print(f"Destination file path length exceeds maximum value of: {max_path_size}")
        raise

    while True:
        if path_size == 0:
            data = file.read(max_path_size)
        else:
            data = file.read(max_path_size - 2 - 32 - path_size)
            
        if not data:
            break
        yield data
