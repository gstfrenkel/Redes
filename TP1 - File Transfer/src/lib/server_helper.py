from lib.server import *

def createServerAndListenStartConnection(args):
    address =  args[args.index('-H') + 1]
    port = args[args.index('-p') + 1]
    server = Server(address, port)
    server.start()

def showServerUsage():
    print('usage: start-server [-h] [-v |-q] [-H ADDR] [-p PORT] [-s DIRPATH]\n\n')
    print('<command description>\n\n')
    print('optional arguments:')
    print('\t-h,--help\tshow this help message and exit')
    print('\t-v,--verbose\tincrease output verbosity')
    print('\t-q,--quiet\tdecrease output verbosity')
    print('\t-H,--host\tservice IP address')
    print('\t-p,--port\tservice port')
    print('\t-s,--storage\tstorage dir path\n')