from socket import *
from threading import * 

class Server:
    def __init__(self, address, port):
        self.address = str(address)
        self.port = int(port)

    def start(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((self.address, self.port))

        self.listen(serverSocket)

    def listen(self, serverSocket: socket):
        while True:
            try:
                message, clientAddress = serverSocket.recvfrom(1024)
                clientThread = Thread(target=self.handleClient, args=(clientAddress, message))
                clientThread.start()

            except Exception as e:
                serverSocket.close()
                raise e
    
    def handleClient(self, clientAddress, message: bytes):
        decodedMessage = message.decode()
        print(f'Client {clientAddress} {decodedMessage}')
        # aca capaz habria que pasar el mensaje por nuestro propio decodificar y ver que al ser un HI, iniciar el triple way handshake

