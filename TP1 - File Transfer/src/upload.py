import sys
from lib.client.client_helper import *

def main(args):
    try:
        useFullArgs = args[1:]
        if '-h' in useFullArgs:
            showUploadUsage()
        else:
            createClientAndUploadToServer(useFullArgs)
                
    except Exception as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)

main(sys.argv)