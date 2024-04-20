import argparse

LOCAL_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 3500


def create_server_parser():
    parser = argparse.ArgumentParser(
        prog="start-server",
        description="<command description>",
    )
    parser.add_argument(
        "-H",
        "--host",
        default=LOCAL_HOST,
        help="service IP address"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_SERVER_PORT,
        help="service port"
    )
    return parser
