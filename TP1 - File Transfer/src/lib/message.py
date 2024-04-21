SYN_TYPE = 1
SYN_OK_TYPE = 2
END_TYPE = 3
END_OK_TYPE = 4
ACK_TYPE = 5
DATA_TYPE = 6
DATA_END_TYPE = 7

class Message:
	def __init__(self, type, seqNumber = 0, data = ""):
		self.type = type
		self.seqNum = seqNumber
		self.data = data

	def encode(self):
		type_bytes = self.type.to_bytes(1, byteorder='big')
		seq_num_bytes = self.seqNum.to_bytes(4, byteorder='big')
		return type_bytes + seq_num_bytes + self.data.encode()
	
	def is_ack(self):
		return self.type == ACK_TYPE

	def is_syn(self):
		return self.type == SYN_TYPE

	def is_syn_ok(self):
		return self.type == SYN_OK_TYPE

	def is_end(self):
		return self.type == END_TYPE

	def is_end_ok(self):
		return self.type == END_OK_TYPE

	def get_data(self):
		return self.data

	def get_message_to_send(self):
		return
	 
	@classmethod
	def decode(cls, messageEncoded: bytes):
		type = messageEncoded[0]
		seqNum = int.from_bytes(messageEncoded[1:5], byteorder='big')
		data = messageEncoded[5:].decode()
		return cls(type, seqNum, data)

	@classmethod
	def new_ack(cls):
		return cls(ACK_TYPE)

	@classmethod
	def new_syn(cls):
		return cls(SYN_TYPE)

	@classmethod
	def new_syn_ok(cls):
		return cls(SYN_OK_TYPE)
	
	@classmethod
	def new_end(cls):
		return cls(END_TYPE)

	@classmethod
	def new_end_ok(cls):
		return cls(END_OK_TYPE)
