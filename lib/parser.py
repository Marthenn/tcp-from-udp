"""
parser.py is a module to parse the argument when running the server or client.
For server the format is python3 server.py [broadcast_port] [path file input].
For client the format is python3 client.py [client_port] [broadcast_port] [path file output].
"""

import argparse


def parse_args(is_server: bool = False):
    """
    Parse the argument when running the server or client.
    :param is_server: whether the program is a server or client
    :return: the port(s) and path file
    """
    if is_server:
        parser = argparse.ArgumentParser(
            description="Server for the file transfer application using UDP"
        )
        parser.add_argument(
            "broadcast_port",
            type=int,
            help="The port to broadcast the file"
        )
        parser.add_argument(
            "path_file",
            type=str,
            help="The path to the file to be sent"
        )
        args = parser.parse_args()
        return args.broadcast_port, args.path_file
    else:
        parser = argparse.ArgumentParser(
            description="Client for the file transfer application using UDP"
        )
        parser.add_argument(
            "client_port",
            type=int,
            help="The port to receive the file"
        )
        parser.add_argument(
            "broadcast_port",
            type=int,
            help="The port to broadcast the file"
        )
        parser.add_argument(
            "path_file",
            type=str,
            help="The path to the file to be received"
        )
        args = parser.parse_args()
        return args.client_port, args.broadcast_port, args.path_file


if __name__ == "__main__":
    print(parse_args(False))
