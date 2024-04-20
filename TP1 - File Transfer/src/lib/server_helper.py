from lib.server import Server


def createServerAndListenStartConnection(server_host, server_port):
    server = Server(server_host, server_port)
    server.start()
