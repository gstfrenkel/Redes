from socket import *
from lib.message import *
from lib.constants import TIMEOUT, MAX_SYN_TRIES, MAX_FIN_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port):
        self.srv_address = str(srv_address)
        self.srv_port = int(srv_port)
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
            print("Maximun SYN tries reached.")
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
            print("Maximun FIN tries reached.")
            return

        if decoded_msg.is_ack():
            self.socket.sendto(Message.new_end_ok().encode(), (self.srv_address, self.srv_port))
            self.socket.close()
            self.connected = False
            print("Disconnected from server.")

    def upload(self):
        return
        message = '1|1|\\|\\' # primer 1 de upload y segundo de ACK

        self.socket.sendto(Message(1, message).encode(), (self.srv_address, self.srv_port)) # aca habria que mandar el upload pero con una flag de conectado
