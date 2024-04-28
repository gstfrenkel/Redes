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
        self.socket.sendto(Message.new_ack().encode(), self.address)


        print(f"file name: {message.data}")
        self.file = open(message.data, "wb+")

        if message.is_upload_type():
            self.upload()
        elif message.is_download_type():
            self.download()

        self.disconnect()

    def connect(self):
        while self.tries < MAX_TRIES:
            
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(enc_msg)
                self.tries = 0
                print(f"Successfully established connection to {self.address[0]}:{self.address[1]}.")
                return message, True
            except timeout:
                self.tries += 1
        print(f"Failed to establish connection to {self.address[0]}:{self.address[1]}. Aborting.")
        return None, False

    def upload(self):
        while True:
            if self.tries == MAX_TRIES:
                break

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.tries += 1
                self.socket.sendto(Message(ACK_TYPE, self.last_seq_num).encode(), self.address)
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
                
            self.socket.sendto(Message(ACK_TYPE, self.last_seq_num).encode(), self.address)


    def download(self):
        while True:
            message, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)




    def disconnect(self):
        if self.file:
            self.file.close()
        self.socket.close()
        print(f"Successfully disconnected from {self.address[0]}:{self.address[1]}.")
            

    

    def process_syn_msg(self, address):
        print(f'Attempt to connect from {address}, sending Ack...')

        try:
            self.socket.sendto(Message.new_ack().encode(), address)
        except timeout:
            print("Timeout waiting for connection confirmation. Disconnecting...")

    def process_syn_ok_msg(self, address):
        print(f'Connection confirmation from {address}. Connection successfully established.')

    def process_end_msg(self, address):
        try:
            print(f'Attempt to disconnect from {address}, sending ACK...')
            self.socket.sendto(Message.new_ack().encode(), address)
        except timeout:
            print("Timeout waiting for disconnection confirmation.")

    def process_end_ok_msg(self, address):
        print(f'Disconnection confirmation from {address}. Connection successfully terminated.')

    def process_data_msg(self, address, message):
        print(f'Data message arrived: type {message.type} seqNumber {message.seq_num}')
 
        self.file.write(message.data.encode())
        self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), address)

    def save_file(self, message, address):
        file_size = message.file_size
        self.file = open(message.file_name, "wb+")
        self.file.write(message.data.encode())
        file_size -= len(message.data)
        self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), address)
        while file_size > 0:
            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)
                print("llego el mensaje", decoded_msg.seq_num)
                if (decoded_msg.is_data_type()):
                    if decoded_msg.seq_num > self.last_seq_num:
                        self.last_seq_num = decoded_msg.seq_num
                        self.file.write(decoded_msg.data.encode())
                        file_size -= len(decoded_msg.data)
                    else:
                        print("llego repetido, solo mandamos el ack")
                    self.socket.sendto(Message(ACK_TYPE, decoded_msg.seq_num).encode(), address)

            except:
                break # esto hay que cambiarlo

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