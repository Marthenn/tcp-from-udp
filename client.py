"""
The module for the client class of the file transfer application using UDP
"""
import sys
import time
from typing import Tuple
from socket import timeout
from lib.parser import parse_args
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import ACK_FLAG, SYN_ACK_FLAG, SYN_FLAG, DEFAULT_IP, FIN_FLAG, TIMEOUT_LISTEN


class Client:
    """
    The client class of the file transfer application using UDP
    The client should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Receives the file from the server
    3. Sends the acknowledgement to the server
    """

    def __init__(self):
        client_port, broadcast_port, output_file, server_ip, client_ip = parse_args(
            False)
        if server_ip is None:
            server_ip = DEFAULT_IP
        if client_ip is None:
            client_ip = DEFAULT_IP
        self.server_ip = server_ip
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.output_file = output_file.split("/")[-1]
        self.file = self.create_file()
        self.conn = Connection(
            ip=client_ip,
            port=self.client_port,
            broadcast=self.broadcast_port,
            as_server=False
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
        self.file.close()

    def connect(self):
        """Connect"""
        self.conn.send(
            self.segment.to_bytes(), self.server_ip, self.conn.broadcast_port
        )

    def acknowledge(self, ack_number: int, server_address: Tuple[str, str]):
        """Send acknowledge to the server"""
        response = Segment()
        response.set_flag(["ACK"])
        response_header = response.get_header()
        response_header["seq"] = ack_number - 1
        response_header["ack"] = ack_number
        response.set_header(response_header)
        self.conn.send(response.to_bytes(),
                       server_address[0], server_address[1])

    def three_way_handshake(self):
        """
        Establishes a three-way handshake connection with the server
        1. Send SYN to server
        2. Receive SYN-ACK from server
        3. Send ACK to server
        """
        while True:
            server_addr = (self.server_ip, self.broadcast_port)
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

    def shutdown(self):
        """Shutdown the client"""
        self.close_file()
        self.conn.close()

    def listen_file_transfer(self):
        """Listen for file transfer attempt from server"""
        # File transfer, client-side, receive file from a server
        # SYN : 0
        # ACK : 1
        # Metadata : 2
        metadata_seq_number = 2
        is_metadata_received = False
        seq_number = 3

        while True:
            try:
                data, server_address = self.conn.listen_segment()
                if server_address[1] != self.broadcast_port:
                    print(
                        f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] Received Segment {self.segment.get_header()['seq']} [Wrong port]"
                    )
                else:
                    self.segment = Segment.from_bytes(data)
                    # Received data fails checksum
                    if not self.segment.is_valid():
                        print(
                            f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] Received Segment {self.segment.get_header()['seq']} [Segment Corrupted]"
                        )
                    # Received valid metadata when metadata haven't been received
                    elif (self.segment.get_header()["seq"] == metadata_seq_number
                            and not is_metadata_received
                          ):
                        payload = self.segment.get_payload()
                        metadata = payload.decode().split(",")
                        print(
                            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Received Filename: {metadata[0]}, File Extension: {metadata[1]}, File Size: {metadata[2]}"
                        )
                        print(
                            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Sending ACK {metadata_seq_number + 1}"
                        )
                        self.acknowledge(self.segment.get_header()[
                                         "seq"], server_address)
                        # Prevent the loop from continuing, which would cause ACK to be sent twice
                        continue
                    # Received valid data that is next in line to be received
                    elif (self.segment.get_header()["seq"] == seq_number
                          ):
                        payload = self.segment.get_payload()
                        print(
                            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Received Segment {seq_number}"
                        )
                        print(
                            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Sending ACK {seq_number + 1}"
                        )
                        self.file.write(payload)
                        seq_number += 1
                        self.acknowledge(seq_number, server_address)
                        # Prevent the loop from continuing, which would cause ACK to be sent twice
                        continue
                    # End of File
                    elif self.segment.get_flag() == FIN_FLAG:
                        print(
                            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Received FIN"
                        )
                        break
                    # Received previously received data
                    elif self.segment.get_header()["seq"] < seq_number:
                        print(
                            f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] Received Segment {self.segment.get_header()['seq']} [Duplicate]"
                        )
                    elif self.segment.get_header()["seq"] > seq_number:
                        print(
                            f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] Received Segment {self.segment.get_header()['seq']} [Out-Of-Order]"
                        )
                    self.acknowledge(seq_number, server_address)

            except timeout:
                print(
                    f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] Received Segment {self.segment.get_header()['seq']} [Timeout]"
                )
                self.acknowledge(seq_number, server_address)

        # Received FIN, sending FIN-ACK
        print(
            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] Sending FIN-ACK")
        fin_ack_segment = Segment()
        fin_ack_segment.set_header({
            "ack": seq_number,
            "seq": seq_number
        })
        fin_ack_segment.set_flag(["ACK", "SEQ"])
        self.conn.send(fin_ack_segment.to_bytes(),
                       server_address[0], server_address[1])
        is_ack_received = False
        time_limit = time.time() + TIMEOUT_LISTEN
        while not is_ack_received:
            try:
                data, server_address = self.conn.listen_segment()
                ack_segment = Segment.from_bytes(data)
                if ack_segment.get_flag() == ACK_FLAG:
                    print(
                        f"[ SUCCESS ] [Server {server_address[0]}:{server_address[1]}] ACK received, closing down connection."
                    )
                    is_ack_received = True
            except timeout:
                if time.time() > time_limit:
                    print(
                        f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] [Timeout] Client waited too long, connection closed."
                    )
                    break
                print(
                    f"[ WARNING ] [Server {server_address[0]}:{server_address[1]}] [Timeout] Resending FIN ACK."
                )
                self.conn.send(fin_ack_segment.to_bytes(),
                               server_address[0], server_address[1])

        # ACK received from server
        print(
            f"[ SUCCESS ] [Server {server_address[0]}:{server_address[1]}] Data received successfuly"
        )
        print(
            f"[ INFO ] [Server {server_address[0]}:{server_address[1]}] File written to received_file/{self.output_file}"
        )


if __name__ == "__main__":
    CLIENT = Client()
    CLIENT.connect()
    CLIENT.three_way_handshake()
    CLIENT.listen_file_transfer()
    CLIENT.shutdown()
