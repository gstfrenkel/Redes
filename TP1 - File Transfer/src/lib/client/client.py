from socket import *
import os
from lib.stop_wait import *
from lib.selective_repeat import *
from lib.message import *
from lib.constants import TIMEOUT, MAX_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name):
        srv_socket = socket(AF_INET, SOCK_DGRAM)
        srv_socket.settimeout(TIMEOUT)

        self.socket = srv_socket
        self.address = (srv_address, int(srv_port))
        self.src_path = src_path
        self.file_name = file_name
        self.tries = 0
        self.seq_num = 0

    def connect(self, message_type):
        while self.tries < MAX_TRIES:
            print(f"Attempting to establish connection with server...")
            self.socket.sendto(Message.new_connect(message_type, self.file_name).encode(), self.address)

            try:
                encoded_msg, address = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)
                print("Llega el seqnum", message.seq_num)
                self.seq_num += 1
                break
            except timeout:
                self.tries += 1
                continue

        if self.tries >= MAX_TRIES:
            print("Failed to establish connection with server.")
            return
        
        print("Successfully established connection with server.")
        self.tries = 0
        self.address = address
        return message


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
        else:
            print("Successfully disconnected from server.")

        self.socket.close()

    def upload(self, protocol):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.src_path)
        file = open(file_path, "rb")

        if protocol == SW:
            handler = StopAndWait(self.socket, self.address, file, self.seq_num)
        else:
            handler = SelectiveRepeat(self.socket, self.address, file, self.seq_num)

        ok, _ = handler.send(file_path)
        file.close()

        if ok:
            print("Successfully uploaded file.")
        else:
            print("Failed to upload file.")


    def download(self, message, protocol):
        file = open(self.src_path, "wb+")
        file.write(message.data)
        if message.is_last_data_type():
            print("Successfully downloaded file.")
            return
        
        if protocol == SW:
            handler = StopAndWait(self.socket, self.address, file, self.seq_num)
        else:
            handler = SelectiveRepeat(self.socket, self.address, file, self.seq_num)
            print("Manda el seqnum", message.seq_num)
            self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)

        
        ok = handler.receive(False)
        if ok:
            print("Successfully downloaded file.")
        else:
            print(f"Failed to download file.")
