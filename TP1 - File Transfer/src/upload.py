import sys
from lib.client.client_helper import createClientAndUploadToServer


def main(args):
    try:
        createClientAndUploadToServer(args)

    except Exception as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)


main(sys.argv)
