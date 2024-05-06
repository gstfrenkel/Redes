from socket import * 
from threading import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, TIMEOUT
from lib.server.server_client import ServerClient
from lib.server.exceptions import ServerParamsFailException
from lib.command_parser import CommandParser
from lib.logger import Logger
import os


class Server:
    def __init__(self, args):
        try:
            parser = CommandParser(args)
            address, port, storage_path, should_be_verbose, show_description = parser.parse_command()

            if show_description:
                help()
                return

            if None in (address, port, storage_path):
                print('\n\nError al inciar, revisar la descripcion del comando')
                help()
                return

            self.logger = Logger(should_be_verbose)
            self.address = str(address)
            self.port = int(port)
            self.storage_path = storage_path if storage_path[len(storage_path) - 1] == '/' else storage_path + '/'

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

                decoded_msg = Message.decode(message)
                if decoded_msg.is_download_type():
                    try:
                        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)) + "/files"), self.storage_path + decoded_msg.data.decode())
                        file = open(file_path, "rb")
                        file.close()
                    except Exception:
                        print(f'No se encontro el archivo {os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)) + "/files"), self.storage_path + decoded_msg.data.decode())}')
                        continue

                client = Thread(target=self.handle_client_msg, args=(address, message))
                client.start()
            except Exception as e:
                print(f"Failed to receive message: {e}")

    def handle_client_msg(self, address, message):
        client = ServerClient(address, self.logger, self.storage_path)
        client.start(Message.decode(message))

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
        