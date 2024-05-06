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

        addr = self.parse_argument('-H', '--host')
        port = self.parse_argument('-p', '--port')
        src_path = self.parse_argument('-s', '--src')
        f_name = self.parse_argument('-n', '--name')

        is_verbose = self.check_if_verbose()
        check_protocol = self.parse_protocol()

        return addr, port, src_path, f_name, is_verbose, check_protocol, False

    def parse_download(self):
        if '-h' in self.args:
            return None, None, None, None, None, None, True

        addr = self.parse_argument('-H', '--host')
        port = self.parse_argument('-p', '--port')
        dest_path = self.parse_argument('-d', '--dst')
        f_name = self.parse_argument('-n', '--name')

        is_verbose = self.check_if_verbose()
        check_protocol = self.parse_protocol()

        return addr, port, dest_path, f_name, is_verbose, check_protocol, False

    def parse_start_server(self):
        if '-h' in self.args:
            return None, None, None, None, True

        address = self.parse_argument('-H', '--host')
        port = self.parse_argument('-p', '--port')
        storage_path = self.parse_argument('-s', '--storage')

        should_be_verbose = self.check_if_verbose()

        return address, port, storage_path, should_be_verbose, False

    def parse_argument(self, first_option, second_option, default=None):
        if first_option in self.args:
            return self.args[self.args.index(first_option) + 1]

        if second_option in self.args:
            return self.args[self.args.index(second_option) + 1]

        return default

    def check_if_verbose(self):
        if self.is_verbose() and not self.is_quiet():
            return True
        return False

    def is_verbose(self):
        return ('-v' in self.args or '--verbose' in self.args)

    def is_quiet(self):
        return ('-q' in self.args or '--quiet' in self.args)

    def parse_protocol(self):
        if '-sw' in self.args and '-sr' not in self.args:
            return SW

        if '-sr' in self.args and '-sw' not in self.args:
            return SR

        return None
