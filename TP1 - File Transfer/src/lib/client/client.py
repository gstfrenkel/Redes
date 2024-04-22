from socket import *
import os
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
        file_path = '/Fiuba/leer/chivo_texto.txt'
        try: 
            file =  open(file_path, "r")
            file_data = file.read()
            file_size = os.path.getsize(file_path)
        except Exception as e:
            self.disconnect()
            raise
        seqNumForMessage = 0
        send_data_try = 0

        print(file_size)
        while send_data_try < 3 and file_size > 0:
            data_length = len(file_data)

            if file_size - data_length <= 0:
                message = Message(6, seqNumForMessage, file_data)
            else:
                message = Message(7, seqNumForMessage, file_data)
            self.socket.sendto(message.encode(), (self.srv_address, self.srv_port))

            self.socket.settimeout(TIMEOUT)

            try:
                print('esperando respuesta')
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decoded_msg = Message.decode(encoded_msg)
                print(decoded_msg.type)
                if decoded_msg.type != 5:
                    send_data_try += 1
                    continue

            except timeout:
                send_data_try += 1
                print("no llego el ACK")
                continue
            print(f"llego ACK del paquete {decoded_msg.seqNum}")
            seqNumForMessage += 1
            send_data_try = 0
            file_size -= data_length
        return
