import sys
from lib.server.server import *

def main(args):
    try:
        useFullArgs = args[1:]
        if '-h' in useFullArgs:
            help()
        else:
            Server(useFullArgs)
                
    except KeyboardInterrupt as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)

main(sys.argv)
