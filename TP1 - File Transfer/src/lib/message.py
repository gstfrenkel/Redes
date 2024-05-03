HEADER_SIZE = 5

# Connection
UPLOAD_TYPE_SW = 1
UPLOAD_TYPE_SR = 2
DOWNLOAD_TYPE_SW = 3
DOWNLOAD_TYPE_SR = 4

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
	def __init__(self, type, seq_num = 0, data = bytes()):
		self.type = type
		self.seq_num = seq_num
		self.data = data

	def encode(self):
		type_bytes = self.type.to_bytes(1, byteorder='big')
		seq_num_bytes = self.seq_num.to_bytes(4, byteorder='big')
		if not isinstance(self.data, bytes):
			return type_bytes + seq_num_bytes + self.data.encode()
		return type_bytes + seq_num_bytes + self.data
	
	def is_ack(self):
		return self.type == ACK_TYPE
	
	def is_upload_type(self):
		return self.type == UPLOAD_TYPE_SW or self.type == UPLOAD_TYPE_SR

	def is_download_type(self):
		return self.type == DOWNLOAD_TYPE_SW or self.type == DOWNLOAD_TYPE_SR

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
		return cls(type, seqNum, messageEncoded[5:])

	@classmethod
	def new_ack(cls, seq_num = 0):
		return cls(ACK_TYPE, seq_num)
	
	@classmethod
	def new_connect(cls, message_type, name):
		return cls(message_type, 0, name)	
	
	@classmethod
	def new_disconnect(cls):
		return cls(END_TYPE, 0)	
