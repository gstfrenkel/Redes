from lib.client.client import Client
from lib.message import (
    UPLOAD_TYPE_SR,
    UPLOAD_TYPE_SW,
    DOWNLOAD_TYPE_SR,
    DOWNLOAD_TYPE_SW
)
from lib.command_parser import CommandParser
from lib.constants import SW
import os


def createClientAndUploadToServer(args):
    parser = CommandParser(args)
    (address,
     port,
     src_path,
     file_name,
     should_be_verbose,
     protocol,
     show_description) = parser.parse_command()

    if show_description:
        showUploadUsage()
        return 0

    if None in (address, port, src_path, file_name, protocol):
        print('\nFailed to start client. Please review program parameters.')
        showUploadUsage()
        return 0

    try:
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)) + "/files", src_path)
        file = open(file_path, "rb")
        file.close()
    except Exception:
        print(f'File not found {file_path}')
        return 0

    client = Client(address, port, src_path, file_name, should_be_verbose)

    if protocol == SW:
        message_type = UPLOAD_TYPE_SW
    else:
        message_type = UPLOAD_TYPE_SR

    client.connect(message_type)
    client.upload(protocol)
    client.disconnect()
    return 0


def createClientAndDownloadFromServer(args):
    parser = CommandParser(args)
    (address,
     port,
     dest_path,
     file_name,
     should_be_verbose,
     protocol,
     show_description) = parser.parse_command()

    if show_description:
        showDownloadUsage()
        return 0

    if None in (address, port, dest_path, file_name, protocol):
        print('\nFailed to start client. Please review program parameters.')
        showDownloadUsage()
        return 0

    dest_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)) + "/files", dest_path)

    client = Client(address, port, dest_path, file_name, should_be_verbose)

    if protocol == SW:
        message_type = DOWNLOAD_TYPE_SW
    else:
        message_type = DOWNLOAD_TYPE_SR

    message = client.connect(message_type)
    if not message or message.is_error_type():
        return 0

    client.download(message, protocol)
    client.disconnect()
    return 0


def showDownloadUsage():
    print(
        'usage: download.py [-h] [-v|-q] ' +
        '[-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]\n')
    print('Arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tserver IP address')
    print('\t-p,--port\tserver port')
    print('\t-d,--dst\tdestination file path')
    print('\t-n,--name\tfile name\n')


def showUploadUsage():
    print('usage: upload.py [-h] [-v|-q] ' +
          '[-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]\n')
    print('Arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tserver IP address')
    print('\t-p,--port\tserver port')
    print('\t-s,--src\tsource file path')
    print('\t-n,--name\tfile name\n')
