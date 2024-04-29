from lib.constants import *
from lib.message import *
from socket import *

class StopAndWait:
    def __init__(self, socket, address, file, seq_num):
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0
        self.seq_num = seq_num

    def receive(self, is_server):
        while self.tries < MAX_TRIES:
            if is_server:
                self.socket.sendto(Message(ACK_TYPE, self.seq_num).encode(), self.address)

            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.tries += 1
                continue

            message = Message.decode(enc_msg)

            if message.is_disconnect() and is_server:
                self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)
                break

            if message.seq_num == self.seq_num + 1:
                self.tries = 0
                self.file.write(message.data.encode())
                self.seq_num = message.seq_num
            else:
                self.tries += 1

            if message.is_last_data_type() and not is_server:
                break
            if not is_server:
                self.socket.sendto(Message(ACK_TYPE, self.seq_num).encode(), self.address)

        return self.tries < MAX_TRIES
