from lib.client import *

def createClientAndUploadToServer(args):
    address = args[args.index('-H') + 1]
    port = args[args.index('-p') + 1]
    client = Client(address, port)
    client.startUploading()
    return 0

def createClientAndDownloadFromServer(args):
    return 0

# Esto debería borrarse y crear el parser de cliente directamente,
# que automáticamente muestra este formato de uso cuando le pasas -h
def showDownloadUsage():
    print('usage: download [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]\n')
    print('<command description>\n')
    print('optional arguments:')
    print('\t-h, --help\tshow this help message and exit')
    print('\t-v, --verbose\tincrease output verbosity')
    print('\t-q, --quiet\tdecrease output verbosity')
    print('\t-H, --host\tserver IP address')
    print('\t-p, --port\tserver port')
    print('\t-d, --dst\tdestination file path')
    print('\t-n, --name\tfile name\n')

# Idem con esto
def showUploadUsage():
    print('usage: upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]\n')
    print('<command description>\n')
    print('optional arguments:')
    print('\t-h, --help\tshow this help message and exit')
    print('\t-v, --verbose\tincrease output verbosity')
    print('\t-q, --quiet\tdecrease output verbosity')
    print('\t-H, --host\tserver IP address')
    print('\t-p, --port\tserver port')
    print('\t-d, --dst\tsource file path')
    print('\t-n, --name\tfile name\n')