from socket import socket, timeout, AF_INET, SOCK_DGRAM
from lib.message import (
    Message,
    ACK_TYPE,
    LAST_DATA_TYPE,
    UPLOAD_TYPE_SW,
    DOWNLOAD_TYPE_SW
)
from lib.constants import TIMEOUT, MAX_MESSAGE_SIZE, MAX_TRIES
import os
from lib.selective_repeat import SelectiveRepeat
from lib.stop_wait import StopAndWait


class ServerClient:
    def __init__(self, address, logger, storage_path):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        cli_socket.settimeout(TIMEOUT)
        self.storage_path = storage_path
        self.logger = logger
        self.socket = cli_socket
        self.address = address
        self.file = None
        self.tries = 0
        self.seq_num = 0

    def start(self, message):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        file_path = self.storage_path + message.data.decode()
        if message.is_upload_type():
            self.file = open(file_path, "wb+")
            self.download(message)
        elif message.is_download_type():
            self.file = open(file_path, "rb")
            self.upload(file_path, message.type)

        self.disconnect()

    def download(self, message):
        if message.type == UPLOAD_TYPE_SW:
            handler = StopAndWait(
                self.socket,
                self.address,
                self.file,
                self.seq_num,
                self.logger
            )
        else:
            handler = SelectiveRepeat(
                self.socket,
                self.address,
                self.file,
                self.seq_num,
                self.logger
            )
            self.socket.sendto(Message.new_ack().encode(), self.address)

        ok = handler.receive(True, message)
        if ok:
            self.logger.print_msg(
                "Successfully uploaded file from "
                f"{self.address[0]}:{self.address[1]}."
            )
        else:
            self.logger.print_msg(
                "Failed to upload file from "
                f"{self.address[0]}:{self.address[1]}."
            )

    def upload(self, file_path, msg_type):
        self.seq_num += 1
        if msg_type == DOWNLOAD_TYPE_SW:
            handler = StopAndWait(
                self.socket,
                self.address,
                self.file,
                self.seq_num,
                self.logger
            )
        else:
            handler = SelectiveRepeat(
                self.socket,
                self.address,
                self.file,
                self.seq_num,
                self.logger
            )

        ok, self.seq_num = handler.send(file_path, True)

        while self.seq_num <= 1 and self.tries < MAX_TRIES:
            self.socket.sendto(
                Message(LAST_DATA_TYPE, self.seq_num, "").encode(),
                self.address
            )
            try:
                encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                message = Message.decode(encoded_msg)

                if message.is_disconnect():
                    self.socket.sendto(
                        Message(ACK_TYPE, message.seq_num).encode(),
                        self.address
                    )
                    break
            except timeout:
                self.tries += 1

        if ok and self.tries < MAX_TRIES:
            self.logger.print_msg(
                "Successfully uploaded file to "
                f"{self.address[0]}:{self.address[1]}."
            )
        else:
            self.logger.print_msg(
                "Failed to upload file to "
                f"{self.address[0]}:{self.address[1]}."
            )

    def disconnect(self):
        if self.file:
            self.file.close()
        self.socket.close()
        self.logger.print_msg(
            "Successfully disconnected from "
            f"{self.address[0]}:{self.address[1]}."
        )
