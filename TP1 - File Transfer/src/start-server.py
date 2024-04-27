import sys
from lib.server.server import *
from lib.server.exceptions import ServerParamsFailException


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
    except ServerParamsFailException:
        print("Error: Some of param/s was not included. please see pyhton3 start-server -h")
        sys.exit(0)


main(sys.argv)
