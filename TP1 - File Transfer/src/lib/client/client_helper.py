from lib.client import *
from lib.client.client import Client
from lib.message import UPLOAD_TYPE, DOWNLOAD_TYPE

def createClientAndUploadToServer(args):
    address =  args[args.index('-H') + 1]
    port = args[args.index('-p') + 1]
    src_path = args[args.index('-s') + 1]
    file_name = args[args.index('-n') + 1]
    client = Client(address, port, src_path, file_name)
    client.connect(UPLOAD_TYPE)
    client.upload()
    client.disconnect()
    return 0

def createClientAndDownloadFromServer(args):
    address =  args[args.index('-H') + 1]
    port = args[args.index('-p') + 1]
    dest_path = args[args.index('-d') + 1]
    file_name = args[args.index('-n') + 1]
    client = Client(address, port, dest_path, file_name)
    message = client.connect(DOWNLOAD_TYPE)
    if not message:
        return 0
    client.download(message)
    client.disconnect()
    return 0

def showDownloadUsage():
    print('usage: download [-h] [-v |-q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]\n\n')
    print('<command description>\n\n')
    print('optional arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tserver IP address')
    print('\t-p,--port\tserver port')
    print('\t-d,--dst\tdestination file path')
    print('\t-n,--name\tfile name\n')

def showUploadUsage():
    print('usage: upload [-h] [-v |-q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]\n\n')
    print('<command description>\n\n')
    print('optional arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tserver IP address')
    print('\t-p,--port\tserver port')
    print('\t-s,--src\tsource file path')
    print('\t-n,--name\tfile name\n')
