import os
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES
from lib.message import (
    Message,
    ACK_TYPE,
    DATA_TYPE,
    LAST_DATA_TYPE,
    HEADER_SIZE
)
from socket import timeout


class StopAndWait:
    def __init__(self, socket, address, file, seq_num, logger):
        self.logger = logger
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0
        self.seq_num = seq_num

    def receive(self, is_server, _):
        self.socket.sendto(
            Message(ACK_TYPE, self.seq_num).encode(),
            self.address
        )

        while self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.logger.print_msg(
                    "Timeout waiting for data package "
                    f"{self.seq_num + 1}. Retrying..."
                )
                self.tries += 1
                continue

            message = Message.decode(enc_msg)
            self.socket.sendto(
                Message(ACK_TYPE, message.seq_num).encode(),
                self.address
            )

            self.logger.print_msg(f"Received {message.seq_num}")

            if message.is_disconnect() and is_server:
                break

            if message.seq_num == self.seq_num + 1:
                self.tries = 0
                self.file.write(message.data)
                self.seq_num = message.seq_num
            else:
                self.tries += 1

            if message.is_last_data_type() and not is_server:
                break

        return self.tries < MAX_TRIES

    def send(self, file_path, _is_server):
        file_size = os.path.getsize(file_path)

        for data in read_file_data(self.file):
            data_size = len(data)

            while self.tries < MAX_TRIES:
                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE

                self.socket.sendto(
                    Message(type, self.seq_num, data).encode(),
                    self.address
                )
                self.logger.print_msg(f'Sending message {self.seq_num}')

                try:
                    encoded_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                    message = Message.decode(encoded_msg)
                    self.logger.print_msg(
                        'Message received'
                        'f{message.seq_num}'
                    )

                    if message.is_disconnect():
                        self.socket.sendto(
                            Message(ACK_TYPE, message.seq_num).encode(),
                            self.address
                        )
                        break

                    if not message.is_ack() or message.seq_num != self.seq_num:
                        self.tries += 1
                        continue
                    self.tries = 0
                except timeout:
                    self.tries += 1
                    self.logger.print_msg(
                        "Timeout waiting for ACK package "
                        f"{self.seq_num}. Retrying..."
                    )
                    continue

                break

            if self.tries >= MAX_TRIES:
                self.logger.print_msg("Failed to upload file.")
                return False, self.seq_num

            self.seq_num += 1
            file_size -= data_size

        return self.tries < MAX_TRIES, self.seq_num


def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
