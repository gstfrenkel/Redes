from socket import * 
from threading import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, TIMEOUT

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
        clientSocket.settimeout(TIMEOUT)
        
        try:
            clientSocket.sendto(Message.newSynAckMessage().encode(), clientAddress)
        except timeout:
            print("Timeout waiting for client SYN_OK. Disconnecting...")

        clientSocket.close()

    def processSynOkMessage(self, clientAddress):
        print(f'SYN_OK message arrived from client {clientAddress}. Connection established')
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.settimeout(TIMEOUT)
        
        self.clients[clientAddress] = clientSocket


    def processFinMessage(self, clientAddress):
        if clientAddress in self.clients:
            clientSocket = self.clients[clientAddress]
        else:
            print(f'FIN message arrived from an unconnected client: {clientAddress}')
            return

        try:
            print(f'FIN message arrived from client {clientAddress}, sending ACK...')
            clientSocket.sendto(Message.newFinAckMessage().encode(), clientAddress)
        except timeout:
            print("Timeout waiting for client FIN_OK")

    def processFinOkMessage(self, clientAddress):
        if clientAddress in self.clients:
            clientSocket = self.clients[clientAddress]
        else:
            print(f'FIN_OK message arrived from an unconnected client: {clientAddress}')
            return

        clientSocket.close()
        del self.clients[clientAddress]
        print(f'FIN_OK message arrived from client {clientAddress}. Disconnection successfully')

    def processDataMessage(self, clientAddress, message):
        if clientAddress not in self.clients:
            print(f"Data message arrived from an unconnected client: {clientAddress}")
            return
        
        print(f'Data message arrived: {message}')
        


    def handleClientMessage(self, clientAddress, message: bytes):        
        message = Message.decode(message)

        if message.isSynMessage():
            self.processSynMessage(clientAddress)

        elif message.isSynOkMessage():
            self.processSynOkMessage(clientAddress)

        elif message.isFinMessage():
            self.processFinMessage(clientAddress)

        elif message.isFinOkMessage():
            self.processFinOkMessage(clientAddress)

        else:
            #self.processDataMessage(clientAddress, message)
            print("aaaa")