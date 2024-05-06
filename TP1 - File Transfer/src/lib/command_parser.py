from lib.constants import SW, SR

class CommandParser:
  def __init__(self, args):
    self.entity = args[0]
    self.args = args
    self.valid_args = True

  def parse_command(self):
    if self.entity == 'upload.py':
        return self.parse_upload()
    elif self.entity == 'download.py':
        return self.parse_download()
    elif self.entity == 'start-server.py':
        return self.parse_start_server()

  def parse_upload(self):
    if '-h' in self.args:
       return None, None, None, None, None, None, True
    
    address =  self.parse_argument('-H', '--host')
    port = self.parse_argument('-p', '--port')
    src_path = self.parse_argument('-s', '--src')
    file_name = self.parse_argument('-n', '--name')

    should_be_verbose = self.check_if_verbose()
    check_protocol = self.parse_protocol()

    return address, port, src_path, file_name, should_be_verbose, check_protocol, False

  def parse_download(self):
    if '-h' in self.args:
      return None, None, None, None, None, None, True
    
    address =  self.parse_argument('-H', '--host')
    port = self.parse_argument('-p', '--port')
    dest_path = self.parse_argument('-d', '--dst')
    file_name = self.parse_argument('-n', '--name')

    should_be_verbose = self.check_if_verbose()
    check_protocol = self.parse_protocol()

    return address, port, dest_path, file_name, should_be_verbose, check_protocol, False
  
  def parse_start_server(self):
    if '-h' in self.args:
      return None, None, None, None, True

    address =  self.parse_argument('-H', '--host')
    port = self.parse_argument('-p', '--port')
    storage_path = self.parse_argument('-s', '--storage')

    should_be_verbose = self.check_if_verbose()

    return address, port, storage_path, should_be_verbose, False
  

  def parse_argument(self, first_option, second_option, default = None):
    if first_option in self.args:
       return self.args[self.args.index(first_option) + 1]
    
    if second_option in self.args:
      return self.args[self.args.index(second_option) + 1]
    
    return default
  
  def check_if_verbose(self): 
    if ('-v' in self.args or '--verbose' in self.args) and not ('-q' in self.args or '--quiet' in self.args):
      return True
    return False
  
  def parse_protocol(self):
    if '-sw' in self.args and not '-sr' in self.args:
      return SW
    
    if '-sr' in self.args and not '-sw' in self.args:
      return SR
    
    return None
