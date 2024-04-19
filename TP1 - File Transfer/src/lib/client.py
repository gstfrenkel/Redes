from socket import *
from lib.messages import SYN_MESSAGE, SYN_ACK_MESSAGE, CONNECTED_MESSAGE, FIN_MESSAGE, FIN_ACK_MESSAGE, DISCONNECTED_MESSAGE
from lib.constants import TIMEOUT, MAX_SYN_TRIES, MAX_FIN_TRIES, MAX_MESSAGE_SIZE

class Client:
    def __init__(self, serverAddress, serverPort):
        self.serverAddress = str(serverAddress)
        self.serverPort = int(serverPort)
        self.connected = False
        self.socket = None

    def connect(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT)

        syn_tries = 0
        while syn_tries < MAX_SYN_TRIES:
            try:
                self.socket.sendto(SYN_MESSAGE.encode(), (self.serverAddress, self.serverPort))
                encondedMessage, serverSocket = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decodedMessage = encondedMessage.decode()
                
                break
            except timeout:
                print("Timeout waiting for server ACK response. Retrying...")
                syn_tries += 1

        if syn_tries == MAX_SYN_TRIES:
            self.socket.close()
            self.socket = None
            print("Maximum SYN tries reached")
            raise KeyboardInterrupt

        if decodedMessage == SYN_ACK_MESSAGE:
            self.socket.sendto(CONNECTED_MESSAGE.encode(), (self.serverAddress, self.serverPort))
            print("Connected to server")
            self.connected = True

    def disconnect(self):
        fin_tries = 0
        while fin_tries < MAX_FIN_TRIES:
            try:
                self.socket.sendto(FIN_MESSAGE.encode(), (self.serverAddress, self.serverPort))
                encondedMessage, serverAddress = self.socket.recvfrom(MAX_MESSAGE_SIZE)
                decodedMessage = encondedMessage.decode()

                break
            except socket.timeout:
                print("Timeout waiting for server ACK response. Retrying...")
                fin_tries += 1

        if fin_tries == MAX_FIN_TRIES:
            print("Maximum FIN tries reached")
            raise KeyboardInterrupt

        if decodedMessage == FIN_ACK_MESSAGE:
            self.socket.sendto(DISCONNECTED_MESSAGE.encode(), (self.serverAddress, self.serverPort))
            self.socket.close()
            self.connected = False
            print("Disconnected from server")

    def startUploading(self):
        message = '1|1|\\|\\' # primer 1 de upload y segundo de ACK
        self.socket.sendto(message.encode(), (self.serverAddress, self.serverPort)) # aca habria que mandar el upload pero con una flag de conectado