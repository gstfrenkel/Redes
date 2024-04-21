from socket import *
from threading import * 
from lib.messages import *
from lib.constants import MAX_MESSAGE_SIZE
import time

class Server:
    def __init__(self, address, port):
        self.address = str(address)
        self.port = int(port)
        self.clients = {}

    def start(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((self.address, self.port))

        self.listen(serverSocket)

    def listen(self, serverSocket: socket):
        while True:
            try:   
                message, clientAddress = serverSocket.recvfrom(MAX_MESSAGE_SIZE)
                clientThread = Thread(target=self.handleClientMessage, args=(clientAddress, message))
                clientThread.start()

            except Exception as e:
                serverSocket.close()
                raise e
    
    def processSynMessage(self, clientAddress):
        print(f'SYN message arrived from client {clientAddress}, sending ACK...')
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.settimeout(0.5)
        
        try:
            clientSocket.sendto(SYN_ACK_MESSAGE.encode(), clientAddress)
        except timeout:
            print("Timeout waiting for client SYN_OK. Disconnecting...")

        clientSocket.close()

    def processSynOkMessage(self, clientAddress):
        print(f'SYN_OK message arrived from client {clientAddress}. Connection established')
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.settimeout(0.5)
        
        self.clients[clientAddress] = clientSocket

    def processFinMessage(self, clientAddress):
        if clientAddress in self.clients:
            clientSocket = self.clients[clientAddress]
        else:
            print(f'FIN message arrived from an unknown client')
            return

        try:
            print(f'FIN message arrived from client {clientAddress}, sending ACK...')
            clientSocket.sendto(FIN_ACK_MESSAGE.encode(), clientAddress)
        except timeout:
            print("Timeout waiting for client FIN_OK")

    def processFinOkMessage(self, clientAddress):
        if clientAddress in self.clients:
            clientSocket = self.clients[clientAddress]
        else:
            print(f'FIN_OK message arrived from an unknown client')
            return

        clientSocket.close()
        del self.clients[clientAddress]
        print(f'FIN_OK message arrived from client {clientAddress}. Disconnection successfully')

    def handleClientMessage(self, clientAddress, message: bytes):
        decodedMessage = message.decode()
        if decodedMessage == SYN_MESSAGE:
            self.processSynMessage(clientAddress)

        elif decodedMessage == CONNECTED_MESSAGE:
            self.processSynOkMessage(clientAddress)

        elif decodedMessage == FIN_MESSAGE:
            self.processFinMessage(clientAddress)

        elif decodedMessage == DISCONNECTED_MESSAGE:
            self.processFinOkMessage(clientAddress)

        else:
            print(decodedMessage)
