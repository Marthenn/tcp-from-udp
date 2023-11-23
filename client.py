"""
The module for the client class of the file transfer application using UDP
"""
import sys
from socket import timeout
from lib.parser import parse_args
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import ACK_FLAG, SYN_ACK_FLAG, SYN_FLAG, DEFAULT_IP


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
        self.output_file = output_file.split("/")[-1]
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
            self.segment.to_bytes(), self.conn.ip, self.conn.broadcast_port
        )

    def three_way_handshake(self):
        """
        Establishes a three-way handshake connection with the server
        1. Send SYN to server
        2. Receive SYN-ACK from server
        3. Send ACK to server
        """
        while True:
            server_addr = (DEFAULT_IP, self.broadcast_port)
            try:
                data, server_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(data)

                if self.segment.get_flag() == SYN_FLAG:
                    self.segment.set_flag(["SYN", "ACK"])
                    header = self.segment.get_header()
                    header["ack"] = header["seq"] + 1
                    header["seq"] = 0
                    self.segment.set_header(header)
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] received SYN from client"
                    )
                    self.conn.send(self.segment.to_bytes(), *server_addr)

                elif self.segment.get_flag() == SYN_ACK_FLAG:
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] sent SYN-ACK to client"
                    )
                    self.conn.send(self.segment.to_bytes(), *server_addr)

                elif self.segment.get_flag() == ACK_FLAG:
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] received ACK from client"
                    )
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] Three-way handshake established"
                    )
                    break

                else:
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] already received segment file, resetting connection"
                    )
                    self.segment.set_flag(["SYN", "ACK"])
                    header = self.segment.get_header()
                    header["ack"] = header["seq"] + 1
                    header["seq"] = 0
                    self.segment.set_header(header)
                    print(
                        f"[ INFO ] [Server {server_addr[0]}:{server_addr[1]}] sent SYN-ACK to client"
                    )
                    self.conn.send(self.segment.to_bytes(), *server_addr)

            except timeout:
                if self.segment.get_flag() == SYN_FLAG:
                    print(
                        f"[ TIMEOUT ] [Server {server_addr[0]}:{server_addr[1]}] ACK response timeout, resending SYN"
                    )
                    self.conn.send(self.segment.to_bytes(), *server_addr)

                else:
                    print(
                        f"[ TIMEOUT ] [Server {server_addr[0]}:{server_addr[1]}] SYN response timeout"
                    )


if __name__ == "__main__":
    CLIENT = Client()
    CLIENT.connect()
    CLIENT.three_way_handshake()
