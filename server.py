"""
The module for the server class of the file transfer application using UDP
"""
import sys
import os
from typing import List
from math import ceil
from socket import timeout
from lib.parser import parse_args
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import SEGMENT_SIZE, PAYLOAD_SIZE, SYN_FLAG, SYN_ACK_FLAG


class Server:
    """
    The server class of the file transfer application using UDP
    The server should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Send the file to the client
    """

    def __init__(self) -> None:
        args = parse_args(True)
        broadcast_port, input_file_path, server_ip = args
        self.ip = server_ip
        self.conn = Connection(
            ip=self.ip,
            broadcast=broadcast_port,
            as_server=True
        )
        self.input_file_path = input_file_path
        self.input_file_name = self.input_file_path.split("/")[-1]
        self.file = self.open_file()
        self.segment = Segment()
        self.segment_list: List[Segment] = []
        self.client_list = []

    def listen_for_clients(self):
        print("[ INFO ] Listening for clients")
        while True:
            try:
                segment, client_addr = self.conn.listen_segment()
                client_ip, client_port = client_addr
                self.client_list.append(client_addr)
                print(
                    f"[ INFO ] Received connection request from client: {client_ip}:{client_port}")

                answer = input(
                    "[ PROMPT ] Do you want to add more clients? (y/n) ")
                while not (answer.lower() in ["y", "n"]):
                    print("[ ERROR ] Invalid input")
                    answer = input(
                        "[ PROMPT ] Do you want to add more clients? (y/n) ")
                if answer.lower() == "n":
                    print("\n[ INFO ] The following clients will be served:")
                    for idx, client in enumerate(self.client_list):
                        print(f"[ INFO ] {idx+1}. {client[0]}:{client[1]}")
                    print()
                    break

            except timeout:
                print("[ TIMEOUT ] Timeout while listening for client, exiting")
                break

    def three_way_handshake(self, client_addr):
        """
        Establishes a three-way handshake connection with the client
        1. Receive SYN from client
        2. Send SYN-ACK to client
        3. Receive ACK from client
        """
        print(
            f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] Initiating three-way handshake"
        )
        self.segment.set_flag(["SYN"])

        while True:
            if self.segment.get_flag() == SYN_FLAG:
                print(
                    f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] sent SYN to server"
                )
                header = self.segment.get_header()
                header["seq"] = 0
                header["ack"] = 0
                self.segment.set_header(header)
                self.conn.send(self.segment.to_bytes(), *client_addr)
                try:
                    data, _ = self.conn.listen_segment()
                    self.segment = Segment.from_bytes(data)
                except timeout:
                    print(
                        f"[ TIMEOUT ] [Client {client_addr[0]}:{client_addr[1]}] ACK response timeout, resending SYN"
                    )

            elif self.segment.get_flag() == SYN_ACK_FLAG:
                print(
                    f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] received SYN-ACK from server"
                )
                print(
                    f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] sent ACK to server"
                )
                header = self.segment.get_header()
                header["seq"] = 1
                header["ack"] = 1
                self.segment.set_header(header)
                self.segment.set_flag(["ACK"])
                self.conn.send(self.segment.to_bytes(), *client_addr)
                break

            else:
                print(
                    f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] is waiting for file already, ending three-way handshake"
                )
                break

        print(
            f"[ INFO ] [Client {client_addr[0]}:{client_addr[1]}] Three-way handshake established"
        )

    def open_file(self):
        """
        Return the file handle of the input file
        """
        try:
            file = open(f"sent_file/{self.input_file_path}", "wb")
            return file
        except FileNotFoundError:
            print(
                f"[!] {self.input_file_path} doesn't exists. Server exiting...")
            sys.exit(1)

    def get_file_size(self):
        """
        Return the size of the input file
        """
        try:
            return os.path.getsize(self.input_file_path)
        except:
            print("Error reading file", self.input_file_path, ". Aborting.")

    def split_file(self):
        """Split the file into segments"""
        # SYN : 0
        # ACK : 1
        # Metadata : 2
        # Data : 3 - n
        metadata_segment = Segment()
        filename = self.input_file_name.split(".")[0]
        extension = self.input_file_name.split(".")[1]
        metadata = filename.encode() + ",".encode() + extension.encode() + \
            ",".encode() + str(self.get_file_size()).encode()
        metadata_segment.set_payload(metadata)
        header = metadata_segment.get_header()
        header["seq"] = 2
        header["ack"] = 0
        metadata_segment.set_header(header)
        self.segment_list.append(metadata_segment)

        segment_count = self.get_segment_count()
        offset = 0
        for i in range(segment_count):
            segment = Segment()

            # Create payload
            offset += PAYLOAD_SIZE
            self.file.seek(offset)
            data_to_set = self.file.read(PAYLOAD_SIZE)
            segment.set_payload(data_to_set)

            # Create header
            header = segment.get_header()
            header["seq"] = i + 3
            header["ack"] = 3
            segment.set_header(header)
            self.segment_list.append(segment)

    def get_segment_count(self):
        """Get how many segment has to be created to sent the given file"""
        return ceil(self.get_file_size() / SEGMENT_SIZE)

    def initiate_transfer(self):
        for client in self.client_list:
            self.three_way_handshake(client)


if __name__ == "__main__":
    SERVER = Server()
    SERVER.listen_for_clients()
    SERVER.initiate_transfer()
