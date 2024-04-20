import sys

from lib.parser import create_server_parser
from lib.server_helper import createServerAndListenStartConnection


def main(args):
    try:
        server_parser = create_server_parser()
        data_parsed = server_parser.parse_args(args)

        server_host = data_parsed.host
        server_port = data_parsed.port

        createServerAndListenStartConnection(server_host, server_port)
    except KeyboardInterrupt as e:
        print(e)
        print("\nExiting...")
        sys.exit(0)


main(sys.argv[1:])
