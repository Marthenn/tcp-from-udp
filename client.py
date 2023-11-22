"""
The module for the client class of the file transfer application using UDP
"""

from lib.parser import parse_args
from lib.connection import Connection
from lib.segment import Segment


class Client:
    """
    The client class of the file transfer application using UDP
    The client should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Receives the file from the server
    3. Sends the acknowledgement to the server
    """

    def __init__(self):
        self.client_port, self.broadcast_port, self.path_file = parse_args(False)
        self.path_file = self.path_file.split("/")[-1]
        self.conn = Connection(
            port=self.client_port, broadcast=self.broadcast_port, as_server=False
        )
        self.segment = Segment()
        # TODO: add file

    def connect(self):
        self.conn.send(
            self.segment.get_payload(), self.conn.ip, self.conn.broadcast_port
        )
