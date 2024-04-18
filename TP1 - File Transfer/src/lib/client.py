from socket import *

class Client:
    def __init__(self, serverAddress, serverPort):
        self.serverAddress = str(serverAddress)
        self.serverPort = int(serverPort)

    def startUploading(self):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        message = '1|1|\\|\\' # primer 1 de upload y segundo de HI
        clientSocket.sendto(message.encode(), (self.serverAddress, self.serverPort)) # aca habria que mandar el upload pero con el Hi
        clientSocket.close() # en vez de terminar aca deberia empezar a escuchar si le responden del HI con un HI_ACK