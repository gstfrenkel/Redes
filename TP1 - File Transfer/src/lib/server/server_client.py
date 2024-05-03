from socket import * 
from lib.stop_wait import * 
from lib.message import * 
from lib.constants import TIMEOUT, MAX_MESSAGE_SIZE, MAX_TRIES
import os
from lib.selective_repeat import *

class ServerClient:
    def __init__(self, address):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        #cli_socket.settimeout(TIMEOUT)

        self.socket = cli_socket
        self.address = address
        self.file = None
        self.tries = 0
        self.seq_num = 0

    def start(self, message):
        if message.is_upload_type():
            self.file = open(message.data.decode(), "wb+")
            self.download(message.type)
        elif message.is_download_type():
            self.file = open(message.data.decode(), "rb")
            self.upload(message.data, message.type)

        self.disconnect()

    def download(self, msg_type):
        if msg_type == UPLOAD_TYPE_SW:
            handler = StopAndWait(self.socket, self.address, self.file, self.seq_num)
        else:
            handler = SelectiveRepeat(self.socket, self.address, self.file, self.seq_num)
            self.socket.sendto(Message.new_ack().encode(), self.address)

        ok = handler.receive(True)
        if ok:
            print(f"Successfully uploaded file from {self.address[0]}:{self.address[1]}.")
        else:
            print(f"Failed to upload file from {self.address[0]}:{self.address[1]}.")
                
    def upload(self, file_path, msg_type):
        if msg_type == DOWNLOAD_TYPE_SW:
            handler = StopAndWait(self.socket, self.address, self.file, self.seq_num)
        else:
            handler = SelectiveRepeat(self.socket, self.address, self.file, self.seq_num)


        self.seq_num += 1

        ok, self.seq_num = handler.send(file_path)

        while self.seq_num <= 1 and self.tries < MAX_TRIES:
            self.socket.sendto(Message(LAST_DATA_TYPE, self.seq_num, "").encode(), self.address)
            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)

                if message.is_disconnect():
                    self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)
                    break
            except timeout:
                self.tries += 1

        if ok and self.tries < MAX_TRIES:
            print(f"Successfully uploaded file to {self.address[0]}:{self.address[1]}.")
        else:
            print(f"Failed to upload file to {self.address[0]}:{self.address[1]}.")

    def disconnect(self):
        if self.file:
            self.file.close()
        self.socket.close()
        print(f"Successfully disconnected from {self.address[0]}:{self.address[1]}.")
            