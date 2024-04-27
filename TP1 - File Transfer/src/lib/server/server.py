from queue import Queue
from socket import * 
from threading import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, TIMEOUT
from lib.server.server_client import ServerClient
from lib.server.exceptions import ServerParamsFailException


class Server:
    def __init__(self, args):
        try:
            address = args[args.index('-H') + 1]
            port = args[args.index('-p') + 1]
            storage_path = args[args.index('-s') + 1]

            self.address = str(address)
            self.storage_path = str(storage_path)
            self.port = int(port)
            self.clients = {}

            self.start()
        except ValueError:
            raise ServerParamsFailException

    def start(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((self.address, self.port))

        self.listen(serverSocket)

    def listen(self, serverSocket: socket):
        while True:
            try:
                message, address = serverSocket.recvfrom(MAX_MESSAGE_SIZE)

                if address not in self.clients:
                    self.clients[address] = Queue()

                    client = Thread(target=self.handle_client_msg, args=(address, self.clients[address], self.storage_path))
                    client.start()

                self.clients[address].put(message)
            except Exception as e:
                print(f"Failed to receive message: {e}")

    def handle_client_msg(self, address, queue, storage_path):
        client = ServerClient()
        client.handle_client_msg(address, queue, storage_path)
        del(self.clients[address])


def help():
    print('usage: start-server [-h] [-v |-q] [-H ADDR] [-p PORT] [-s DIRPATH]\n\n')
    print('<command description>\n\n')
    print('optional arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tservice IP address')
    print('\t-p,--port\tservice port')
    print('\t-s,--storage\tstorage dir path\n')
        