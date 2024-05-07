from socket import *
import os
from lib.logger import Logger
from lib.stop_wait import *
from lib.selective_repeat import *
from lib.message import *
from lib.constants import TIMEOUT, MAX_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, srv_address, srv_port, src_path, file_name, show_msgs):
        self.logger = Logger(show_msgs)
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
            self.logger.print_msg(f"Attempting to establish connection with server...")
            self.socket.sendto(Message.new_connect(message_type, self.file_name).encode(), self.address)

            try:
                encoded_msg, address = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)
                self.seq_num += 1
                break
            except timeout:
                self.tries += 1
                continue

        if self.tries >= MAX_TRIES:
            self.logger.print_msg("Failed to establish connection with server.")
            return
        
        if message.is_error_type():
            self.logger.print_msg('\nFile not found by the server\n')
            return message
        
        self.logger.print_msg("Successfully established connection with server.")
        self.tries = 0
        self.address = address
        return message


    def disconnect(self):
        while self.tries < MAX_TRIES:
            print('sending disconnect')
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
            self.logger.print_msg("Failed to cleanly disconnect from server.")
        else:
            self.logger.print_msg("Successfully disconnected from server.")

        self.socket.close()

    def upload(self, protocol):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/files", self.src_path)
        file = open(file_path, "rb")

        if protocol == SW:
            handler = StopAndWait(self.socket, self.address, file, self.seq_num, self.logger)
        else:
            handler = SelectiveRepeat(self.socket, self.address, file, self.seq_num, self.logger)

        ok, _ = handler.send(file_path, False)
        file.close()

        if ok:
            self.logger.print_msg("Successfully uploaded file.")
        else:
            self.logger.print_msg("Failed to upload file.")


    def download(self, message, protocol):
        os.makedirs(os.path.dirname(self.src_path), exist_ok=True)
        file = open(self.src_path, "wb+")

        if protocol == SW:
            file.write(message.data)
            if message.is_last_data_type():
                self.logger.print_msg("Successfully downloaded file.")
                return
        
            handler = StopAndWait(self.socket, self.address, file, self.seq_num, self.logger)
        else:
            handler = SelectiveRepeat(self.socket, self.address, file, self.seq_num, self.logger)
        
        ok = handler.receive(False, message)
        if ok:
            self.logger.print_msg("Successfully downloaded file.")
        else:
            self.logger.print_msg(f"Failed to download file.")
