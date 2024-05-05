import sys
from lib.server.server import Server
from lib.server.exceptions import ServerParamsFailException


def main(args):
    try:
        Server(args)

    except KeyboardInterrupt as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)
    except ServerParamsFailException:
        print("Error: Some of param/s was not included.")
        sys.exit(0)


main(sys.argv)
