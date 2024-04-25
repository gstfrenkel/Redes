from socket import * 
from lib.message import * 
from lib.constants import TIMEOUT

class ServerClient:
    def __init__(self):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        cli_socket.settimeout(TIMEOUT)

        self.handshake_complete = False
        self.connection_ended = False
        self.syn_received = False
        self.fin_received = False
        self.socket = cli_socket
        self.file = None
        self.last_seq_num = 0

    def start(self):
        srv_socket = socket(AF_INET, SOCK_DGRAM)
        srv_socket.bind((self.address, self.port))

        self.listen(srv_socket)

    def handle_client_msg(self, address, queue):
        while not self.connection_ended:
            message = Message.decode(queue.get())

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
            else:
                self.process_data_msg(address, message)

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

        # Deberiamos mandar la longitud del file y esperar que lleguen todos los bytes para escribir? 

        if message.is_upload_type():
            self.file = open(message.file_name, "wb+")
            self.file.write(message.data.encode())
            self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), address)
        
        elif message.is_download_type():
            self.file = open(message.file_name, "rb")
            for data in read_file_data(file, 0):
                data_size = len(data)
                tries = 0

                while tries < 3:
                    self.socket.sendto(Message(DATA_TYPE, message.seq_num, data).encode(), address)

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

        else:
            self.file.write(message.data.encode())
            self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), address)


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