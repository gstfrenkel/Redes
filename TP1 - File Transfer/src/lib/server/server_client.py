from socket import * 
from lib.message import * 
from lib.constants import TIMEOUT

class ServerClient:
    def __init__(self):
        cli_socket = socket(AF_INET, SOCK_DGRAM)
        cli_socket.settimeout(TIMEOUT)

        self.handshake_complete = False
        self.connection_ended = False
        self.syn_received = False
        self.fin_received = False
        self.socket = cli_socket

    def start(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((self.address, self.port))

        self.listen(serverSocket)

    def handleClientMessage(self, address, queue):
        while not self.connection_ended:
            message = Message.decode(queue.get())

            if message.isSyn():
                self.processSynMessage(address)
                self.syn_received = True
            elif message.isSynOk():
                if not self.syn_received:
                    print("Unable to complete handshake until Syn is first received.")
                    continue
                self.processSynOkMessage(address)
                self.handshake_complete = True
            elif not self.handshake_complete:
                print(f"Unable to process message until {address} completes handshake.")
                continue
            elif message.isEnd():
                self.processFinMessage(address)
                self.fin_received = True
            elif message.isEndOk():
                if not self.fin_received:
                    print("Unable to complete handshake until Syn is first received.")
                    continue
                self.processFinOkMessage(address)
                self.connection_ended = True
            else:
                self.processDataMessage(address, message)

        self.socket.close()

    def processSynMessage(self, address):
        print(f'SYN message arrived from client {address}, sending ACK...')

        try:
            self.socket.sendto(Message.newAck().encode(), address)
        except timeout:
            print("Timeout waiting for client SYN_OK. Disconnecting...")


    def processSynOkMessage(self, address):
        print(f'SYN_OK message arrived from client {address}. Connection established')


    def processFinMessage(self, address):
        try:
            print(f'FIN message arrived from client {address}, sending ACK...')
            self.socket.sendto(Message.newAck().encode(), address)
        except timeout:
            print("Timeout waiting for client FIN_OK")


    def processFinOkMessage(self, address):
        print(f'FIN_OK message arrived from client {address}. Disconnection successfully')

    def processDataMessage(self, address, message):
        print(f'Data message arrived: {message}')
