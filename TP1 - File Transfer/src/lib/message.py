SYN_TYPE = 1
SYN_OK_TYPE = 2
END_TYPE = 3
END_OK_TYPE = 4
ACK_TYPE = 5
DATA_TYPE = 6
UPLOAD_TYPE = 7
DOWNLOAD_TYPE = 8
LAST_DATA_TYPE = 9

class Message:
	def __init__(self, type, seq_num = 0, data = "", file_name = "", file_size_left = 0):
		self.type = type
		self.seq_num = seq_num
		self.path_size = len(file_name)
		self.file_name = file_name
		self.file_size_left = file_size_left
		self.data = data

	def encode(self):
		type_bytes = self.type.to_bytes(1, byteorder='big')
		seq_num_bytes = self.seq_num.to_bytes(4, byteorder='big')

		if self.is_upload_type():
			path_len_bytes = self.path_size.to_bytes(2, byteorder='big')
			return type_bytes + seq_num_bytes + path_len_bytes + self.file_name.encode() + self.data.encode()
		
		elif self.is_download_type():
			path_len_bytes = self.path_size.to_bytes(2, byteorder='big')
			return type_bytes + seq_num_bytes + path_len_bytes +  self.file_name.encode() + self.data.encode()
		
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
	
	def is_upload_type(self):
		return self.type == UPLOAD_TYPE

	def is_download_type(self):
		return self.type == DOWNLOAD_TYPE

	def is_data_type(self):
		return self.type == DATA_TYPE
	
	def get_data(self):
		return self.data

	def get_message_to_send(self):
		return
	 
	@classmethod
	def decode(cls, messageEncoded: bytes):
		type = messageEncoded[0]
		seqNum = int.from_bytes(messageEncoded[1:5], byteorder='big')

		if type == UPLOAD_TYPE:
			path_size = int.from_bytes(messageEncoded[5:7], byteorder='big')
			path = messageEncoded[7:path_size+7].decode()
			data = messageEncoded[path_size+7:].decode()
			return cls(type, seqNum, data, path)
			
		elif type == DOWNLOAD_TYPE:
			# file_size = int.from_bytes(messageEncoded[5:37], byteorder='big')
			# data = messageEncoded[37:].decode()
			# return cls(type, seqNum, data, "", file_size)
			path_size = int.from_bytes(messageEncoded[5:7], byteorder='big')
			path = messageEncoded[7:path_size+7].decode()
			data = messageEncoded[path_size+7:].decode()
			return cls(type, seqNum, data, path)

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
