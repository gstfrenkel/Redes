SYN_TYPE = int.from_bytes(b'\x01')
SYN_OK_TYPE = int.from_bytes(b'\x02')
END_TYPE = int.from_bytes(b'\x03')
END_OK_TYPE = int.from_bytes(b'\x04')
ACK_TYPE = int.from_bytes(b'\x05')
DATA_TYPE = int.from_bytes(b'\x06')
DATA_END_TYPE = int.from_bytes(b'\x06')

class Message:
	def __init__(self, type, seqNumber = 0, data = ""):
		self.type = type
		self.seqNum = seqNumber
		self.data = data

	def encode(self):
		type_bytes = self.type.to_bytes(1, byteorder='big')
		seq_num_bytes = self.seqNum.to_bytes(4, byteorder='big')
		return type_bytes + seq_num_bytes + self.data.encode()
	
	def isAck(self):
		return self.type == ACK_TYPE

	def isSyn(self):
		return self.type == SYN_TYPE

	def isSynOk(self):
		return self.type == SYN_OK_TYPE

	def isEnd(self):
		return self.type == END_TYPE

	def isEndOk(self):
		return self.type == END_OK_TYPE

	def getMessageData(self):
		return self.data

	def getMessageToSend(self):
		return
	 
	@classmethod
	def decode(cls, messageEncoded: bytes):
		type = messageEncoded[0]
		seqNum = int.from_bytes(messageEncoded[1:5], byteorder='big')
		data = messageEncoded[5:].decode()
		return cls(type, seqNum, data)

	@classmethod
	def newAck(cls):
		return cls(ACK_TYPE)

	@classmethod
	def newSyn(cls):
		return cls(SYN_TYPE)

	@classmethod
	def newSynOk(cls):
		return cls(SYN_OK_TYPE)
	
	@classmethod
	def newEnd(cls):
		return cls(END_TYPE)

	@classmethod
	def newEndOk(cls):
		return cls(END_OK_TYPE)
