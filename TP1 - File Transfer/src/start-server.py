import sys
from lib.server_helper import *

def main(args):
    try:
        useFullArgs = args[1:]
        if '-h' in useFullArgs:
            showServerUsage()
        else:
            createServerAndListenStartConnection(useFullArgs)
                
    except KeyboardInterrupt as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)

main(sys.argv)