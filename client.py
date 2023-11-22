"""
The module for the client class of the file transfer application using UDP
"""
import sys
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
        client_port, broadcast_port, output_file = parse_args(False)
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.output_file = self.output_file.split("/")[-1]
        self.file = self.create_file()
        self.conn = Connection(
            port=self.client_port, broadcast=self.broadcast_port, as_server=False
        )
        self.segment = Segment()

    def create_file(self):
        """Create the output file"""
        try:
            file = open(f"received_file/{self.output_file}", "wb")
            return file
        except FileNotFoundError:
            print(f"[!] {self.output_file} doesn't exists. Client exiting...")
            sys.exit(1)

    def close_file(self):
        """Close the output file"""
        self.output_file.close()

    def connect(self):
        """Connect"""
        self.conn.send(
            self.segment.get_payload(), self.conn.ip, self.conn.broadcast_port
        )
