HEADER_SIZE = 5

# Connection
UPLOAD_TYPE = 1
DOWNLOAD_TYPE = 2

# Data exchange
DATA_TYPE = 3
LAST_DATA_TYPE = 4

# Validation
ACK_TYPE = 5

# Disconnection
END_TYPE = 6

# Message structure
#   1  |    4    | ...
# type | seq_num | data 

class Message:
	def __init__(self, type, seq_num = 0, data = ""):
		self.type = type
		self.seq_num = seq_num
		self.data = data

	def encode(self):
		type_bytes = self.type.to_bytes(1, byteorder='big')
		seq_num_bytes = self.seq_num.to_bytes(4, byteorder='big')		
		return type_bytes + seq_num_bytes + self.data.encode()
	
	def is_ack(self):
		return self.type == ACK_TYPE
	
	def is_upload_type(self):
		return self.type == UPLOAD_TYPE

	def is_download_type(self):
		return self.type == DOWNLOAD_TYPE

	def is_last_data_type(self):
		return self.type == LAST_DATA_TYPE
	
	def is_disconnect(self):
		return self.type == END_TYPE
	
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
	def new_ack(cls, seq_num = 0):
		return cls(ACK_TYPE, seq_num)
	
	@classmethod
	def new_connect(cls, message_type, name):
		return cls(message_type, 0, name)	
	
	@classmethod
	def new_disconnect(cls):
		return cls(END_TYPE, 0, "")	
