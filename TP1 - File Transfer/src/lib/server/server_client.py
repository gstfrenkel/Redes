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

        if not self.file:
            self.file = open(message.file_name, "wb+")
            
        self.file.write(message.data.encode())
        self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), address)
