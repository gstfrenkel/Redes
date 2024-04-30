from socket import * 
from threading import * 
from lib.message import * 
from lib.constants import MAX_MESSAGE_SIZE, MAX_TRIES, TIMEOUT
from queue import Queue
import time
import os

WINDOW_SIZE = 4

class SelectiveRepeat ():
    def __init__(self, socket, address, file, seq_num):
        self.socket = socket
        self.address = address
        self.file = file
        self.tries = 0
        self.seq_num = seq_num

        self.pendings = {}  # Set de ACKs (seqnum) con (Data, timestamp, tries)
        self.abort = False
        self.disconnected = False




        """ # para el que manda
        self.messages_sent = {} # clave: seq_num, valor: mensaje
        self.amount_message_send = 4 # cantidad de mensajes que le quedan disponibles para mandar
        self.messages_to_resend = Queue() # los seqnums de los mensajes que hay que volver a enviar

        # para el que recive
        self.ack_seq_num_received = set()
        self.buffer = [] # aca se van a ir guardando los que lleguen desordenados
        self.window_size = 4 # window size del receptor"""
    
    # Sender
    def send(self, file_path):
        thread_recv_acks = Thread(target=self.recv_acks, args=())
        thread_check_timeouts = Thread(target=self.check_timeouts, args=())
        thread_recv_acks.start()
        thread_check_timeouts.start()

        file_size = os.path.getsize(file_path)

        for data in read_file_data(self.file):
            data_size = len(data)
            while not self.abort and not self.disconnected:
                if len(self.pendings) == WINDOW_SIZE:
                    continue

                type = DATA_TYPE
                if file_size - data_size <= 0:
                    type = LAST_DATA_TYPE
                message = Message(type, self.seq_num, data).encode()
                self.socket.sendto(message, self.address)
                self.pendings[self.seq_num] = (message, time.time(), 0)
                self.seq_num += 1
                file_size -= data_size

            if self.abort:
                break

        thread_recv_acks.join()
        thread_check_timeouts.join()

        if not self.abort and self.disconnected:
            self.socket.sendto(Message(ACK_TYPE, message.seq_num).encode(), self.address)

        return not self.abort

    def recv_acks(self):
        while not self.abort and not self.disconnected:
            enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            message = Message.decode(enc_msg)
            if message.is_ack() and message.seq_num in self.pendings:
                del self.pendings[message.seq_num]                  # Chequear de bloquear el thread entre el borrado y el editado del mensaje pendiente
            elif message.is_disconnect():
                self.disconnected = True
        return
        
    def check_timeouts(self):
        while not self.abort and not self.disconnected:
            for key, val in self.pendings:
                if time.time() - val[1] >= TIMEOUT:
                    if val[2] >= MAX_TRIES:
                        self.abort = True
                        break
                    self.socket.sendto(val[0], self.address)
                    self.pendings[key] = (val[0], time.time(), val[2] + 1)  # Chequear de usar locks!
        return        
    
    def get_message_to_send(self):
        # si no hay en nada en la queue para reenviar, armo un mensaje con la siguiente data
        # si hay algo en la queue para reenviar, reenvio ese mensaje que se perdio
        return
    

    # receiver
    def receive(self, is_server):
        while not self.abort and self.tries < MAX_TRIES:
            try:
                enc_msg, _ = self.socket.recvfrom(MAX_MESSAGE_SIZE)
            except timeout:
                self.tries += 1
                continue
            self.tries = 0
            message = Message.decode(enc_msg)
            if is_server or not message.is_last_data_type():
                self.socket.sendto(Message.new_ack(message.seq_num), self.address)

            if message.seq_num > self.seq_num + 1:      # Si llega un data posterior al que se necesita.
                self.pendings[message.seq_num] = message.data
                continue
            if message.seq_num != self.seq_num + 1:     # Si es un data repetido.
                continue

            self.file.write(message.data.encode())
            self.abort = message.is_last_data_type()
            self.seq_num += 1

            while self.seq_num in self.pendings:
                self.file.write(self.pendings[self.seq_num].encode())
                self.abort = self.pendings[self.seq_num].is_last_data_type()
                self.seq_num += 1       

      
def read_file_data(file):
    while True:
        data = file.read(MAX_MESSAGE_SIZE - HEADER_SIZE)

        if not data:
            break
        yield data
