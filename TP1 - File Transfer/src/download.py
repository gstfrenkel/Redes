import sys
from lib.client.client_helper import createClientAndDownloadFromServer


def main(args):
    try:
        createClientAndDownloadFromServer(args)

    except Exception as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)


main(sys.argv)
