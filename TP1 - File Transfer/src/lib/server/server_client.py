from socket import socket, AF_INET, SOCK_DGRAM
from lib.stop_wait import StopAndWait
from lib.message import Message
from lib.message import UPLOAD_TYPE_SW, DOWNLOAD_TYPE_SW
from lib.message import LAST_DATA_TYPE, ACK_TYPE
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES
from lib.selective_repeat import SelectiveRepeat
import os


class ServerClient:
    def __init__(self, address, logger, storage_path):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        self.storage_path = storage_path
        self.logger = logger
        self.socket = cli_socket
        self.address = address
        self.file = None
        self.tries = 0
        self.seq_num = 0

    def start(self, message):
        relative_path = os.path.dirname(os.path.abspath(__file__)) + "/files"
        storage_path_file_name = self.storage_path + message.data.decode()
        file_path = os.path.join(relative_path, storage_path_file_name)
        if message.is_upload_type():
            self.file = open(file_path, "wb+")
            self.download(message)
        elif message.is_download_type():
            self.file = open(file_path, "rb")
            self.upload(file_path, message.type)

        self.disconnect()

    def download(self, message):
        a_socket = self.socket
        address = self.address
        file = self.file
        seq_num = self.seq_num
        logger = self.logger
        if message.type == UPLOAD_TYPE_SW:
            handler = StopAndWait(a_socket, address, file, seq_num, logger)
        else:
            handler = SelectiveRepeat(a_socket, address, file, seq_num, logger)
            self.socket.sendto(Message.new_ack().encode(), self.address)

        ok = handler.receive(True, message)
        ip_addr = self.address[0]
        port_addr = self.address[1]
        if ok:
            self.logger.client_successfully_uploaded_msg(ip_addr, port_addr)
        else:
            self.logger.client_failed_to_upload_msg(ip_addr, port_addr)

    def upload(self, file_path, msg_type):
        self.seq_num += 1
        logger = self.logger
        file = self.file
        address = self.address
        a_socket = self.socket
        seq_num = self.seq_num

        if msg_type == DOWNLOAD_TYPE_SW:
            handler = StopAndWait(a_socket, address, file, seq_num, logger)
        else:
            handler = SelectiveRepeat(a_socket, address, file, seq_num, logger)

        ok, self.seq_num = handler.send(file_path, True)

        while self.seq_num <= 1 and self.tries < MAX_TRIES:
            last_data_message = Message(LAST_DATA_TYPE, self.seq_num, "")
            self.socket.sendto(last_data_message.encode(), address)
            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)

                if message.is_disconnect():
                    ack_message = Message(ACK_TYPE, message.seq_num)
                    self.socket.sendto(ack_message.encode(), address)
                    break
            except TimeoutError:
                self.tries += 1

        ip_addr = address[0]
        port_addr = address[1]

        if ok and self.tries < MAX_TRIES:
            logger.client_successfully_uploaded_msg(ip_addr, port_addr)
        else:
            logger.client_failed_to_upload_msg(ip_addr, port_addr)

    def disconnect(self):
        ip_addr = self.address[0]
        port_addr = self.address[1]

        if self.file:
            self.file.close()
        self.socket.close()

        self.logger.client_successfully_disconnected_msg(ip_addr, port_addr)
