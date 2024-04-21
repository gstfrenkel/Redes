from queue import Queue
from socket import * 
from threading import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, TIMEOUT
from lib.server.server_client import ServerClient

class Server:
    def __init__(self, args):
        address =  args[args.index('-H') + 1]
        port = args[args.index('-p') + 1]

        self.address = str(address)
        self.port = int(port)
        self.clients = {}

        self.start()

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

                    client = Thread(target=self.handleClientMessage, args=(address, self.clients[address]))
                    client.start()

                self.clients[address].put(message)
            except Exception as e:
                print(f"Failed to receive message: {e}")

    def handleClientMessage(self, address, queue):
        client = ServerClient()
        client.handleClientMessage(address, queue)
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
        