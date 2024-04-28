from socket import * 
from lib.message import * 
from lib.constants import TIMEOUT
from lib.constants import TIMEOUT, MAX_SYN_TRIES, MAX_FIN_TRIES, MAX_MESSAGE_SIZE
import os

class ServerClient:
    def __init__(self):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        #cli_socket.settimeout(TIMEOUT)

        self.handshake_complete = False
        self.connection_ended = False
        self.syn_received = False
        self.fin_received = False
        self.socket = cli_socket
        self.file = None
        self.last_seq_num = 0
        self.is_client_downloading = False

    def handle_client_msg(self, address, queue, server_storage_path):
        while not self.connection_ended:
            message = Message.decode(queue.get())
            print("llego un nuevo mensaje al general")

            if message.is_syn():
                self.process_syn_msg(address)
                self.syn_received = True
            elif message.is_syn_ok():
                if not self.syn_received:
                    print("Unable to complete handshake until Syn is first received.")
                    continue
                self.process_syn_ok_msg(address)
                self.handshake_complete = True
            elif not self.handshake_complete:
                print(f"Unable to process message until {address} completes handshake.")
                continue
            elif message.is_end():
                self.process_end_msg(address)
                self.fin_received = True
            elif message.is_end_ok():
                if not self.fin_received:
                    print("Unable to complete handshake until Syn is first received.")
                    continue
                self.process_end_ok_msg(address)
                self.connection_ended = True
            elif message.is_upload_type():
                self.save_file(message, address, server_storage_path)
            elif message.is_download_type():
                self.send_file_to_client(message, address, server_storage_path)
            else:
                print('ENTRO', message.type)
                # NO SE ESTA USANDO ESTA FUNCION
                # self.process_data_msg(address, message)

        self.socket.close()
        if self.file:
            self.file.close()

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

    def save_file(self, message, address, server_storage_path):
        file_size = message.file_size
        new_file_path = self._create_path_file(server_storage_path, message.file_name)
        self.file = open(new_file_path, "wb+")
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

    # Posible TODO: se podría manejar errores
    def _create_path_file(self, server_storage_path, file_name):
        return server_storage_path + file_name

    def send_file_to_client(self, message, address, server_storage_path):
        file_name = message.file_name
        file_name = self._create_path_file(server_storage_path, file_name)
        file_size = os.path.getsize(file_name)

        with open(file_name, "r") as file:
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

