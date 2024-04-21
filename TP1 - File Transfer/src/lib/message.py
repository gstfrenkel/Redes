SYN_MESSAGE = 'SYN'
SYN_ACK_MESSAGE = 'SYN_ACK'
SYN_OK_MESSAGE = 'SYN_OK'
FIN_MESSAGE = 'FIN'
FIN_ACK_MESSAGE = 'FIN_ACK'
FIN_OK_MESSAGE = 'FIN_OK'
DATA_ACK_MESSAGE = 'ACK'

class Message:
	def __init__(self, seqNumber, data):
		self.seqNum = seqNumber
		self.data = data

	def encode(self):
		seq_num_bytes = self.seqNum.to_bytes(4, byteorder='big')
		return seq_num_bytes + self.data.encode()

	def isSynMessage(self):
		return self.data == SYN_MESSAGE

	def isSynAckMessage(self):
		return self.data == SYN_ACK_MESSAGE

	def isSynOkMessage(self):
		return self.data == SYN_OK_MESSAGE

	def isFinMessage(self):
		return self.data == FIN_MESSAGE

	def isFinAckMessage(self):
		return self.data == FIN_ACK_MESSAGE

	def isFinOkMessage(self):
		return self.data == FIN_OK_MESSAGE

	def getMessageData(self):
		return self.data

	def getMessageToSend(self):
		return
	 
	@classmethod
	def decode(cls, messageEncoded: bytes):
		seqNum = int.from_bytes(messageEncoded[:4], byteorder='big')
		data = messageEncoded[4:].decode()
		return cls(seqNum, data)

	@classmethod
	def newSynMessage(cls):
		return cls(0, SYN_MESSAGE)

	@classmethod
	def newSynAckMessage(cls):
		return cls(0, SYN_ACK_MESSAGE)

	@classmethod
	def newSynOkMessage(cls):
		return cls(0, SYN_OK_MESSAGE)
	
	@classmethod
	def newFinMessage(cls):
		return cls(0, FIN_MESSAGE)

	@classmethod
	def newFinAckMessage(cls):
		return cls(0, FIN_ACK_MESSAGE)

	@classmethod
	def newFinOkMessage(cls):
		return cls(0, FIN_OK_MESSAGE)

	@classmethod
	def newDataAckMessage(cls):
		return cls(0, DATA_ACK_MESSAGE)

