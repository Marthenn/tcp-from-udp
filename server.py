"""
The module for the server class of the file transfer application using UDP
"""
import sys
import os
from typing import List
from math import ceil
from lib.parser import parse_args
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import SEGMENT_SIZE, PAYLOAD_SIZE


class Server :
    """
    The server class of the file transfer application using UDP
    The server should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Send the file to the client
    """
    def __init__(self) -> None:
        args = parse_args(True)
        broadcast_port, input_file_path = args    
        self.conn = Connection(broadcast=broadcast_port, as_server=True)
        self.input_file_path = input_file_path
        self.input_file_name = self.input_file_path.split("/")[-1]
        self.file = self.open_file()
        self.segment_list : List[Segment] = []

    def listen_for_clients(self) :
        self.client_list = []
        while True:
            try :
                segment, client_addr = self.conn.listen_segment()
                client_ip, client_port = client_addr
                client_segment = Segment.from_bytes(segment)
                flag = client_segment.get_flag()
                if flag == 2 : # Flag SYN
                    print("Got request from client :", client_ip, client_port)
                    cont = input("Continue listening ? y/n").lower()
                    while cont != 'y' and cont != 'n' :
                        print("Input not valid")
                        cont = input("Continue listening ? y/n").lower()
                    print("Initiating three way handshake")
                    if self.three_way_handshake(client_ip, client_port) :
                        print("Three way handshake successful. Saving connection.")
                        self.client_list.append(client_addr)
                    else :
                        print("Three way handshake failed. Aborting connection.")
                    if cont == 'n' :
                        print("Stop searching for client. Exiting process")
                        break
                else :
                    print("Didn't receive SYN flag, can't start three way handshake")
            except TimeoutError :
                print("Timeout listening to client. Aborting")
                break
    
    def three_way_handshake(self, client_ip : str, client_port : int) -> bool :
        """
        Melakukan three_way_handshake dari sisi server, diasumsikan server sudah menerima flag "SYN" dari client
        """
        print ("Initiating handshake with client :", client_ip, client_port)
        segment = Segment()
        segment.set_flag(["SYN", "ACK"])
        header = segment.get_header()
        header["seq"] = 0
        header["ack"] = 0
        self.conn.send(segment.to_bytes(), client_ip, client_port)
        try : 
            validSegment = False
            while (not(validSegment)) :
                ack, clientAddr = self.conn.listen_segment()
                ackSegment = Segment.from_bytes(ack)
                if clientAddr[0] != client_ip or clientAddr[1] != client_port : # Bukan dari client yang bersangkutan
                    print("Wrong client, listening again")
                elif ackSegment.get_flag() < 16 : # Bukan flag ACK
                    print("Wrong flag. Aborting handshake")
                    return False
                else :
                    validSegment = True
                    print("Received ACK from client :", client_ip, client_port, ". Connection established.")
            return True
        except TimeoutError :
            print("Waiting for ACK from client :", client_ip, client_port, "timed out. Aborting connection")
            return False

    def open_file(self) :
        """
        Return the file handle of the input file
        """
        try:
            file = open(f"sent_file/{self.input_file_path}", "wb")
            return file
        except FileNotFoundError:
            print(f"[!] {self.input_file_path} doesn't exists. Server exiting...")
            sys.exit(1)

    def get_file_size(self) :
        """
        Return the size of the input file
        """
        try :
            return os.path.getsize(self.input_file_path)
        except:
            print("Error reading file", self.input_file_path, ". Aborting.")

    def split_file(self):
        """Split the file into segments"""
        metadata_segment = Segment()
        filename = self.input_file_name.split(".")[0]
        extension = self.input_file_name.split(".")[1]
        metadata = filename.encode() + ",".encode() + extension.encode() + ",".encode() + str(self.get_file_size()).encode()
        metadata_segment.set_payload(metadata)
        header = metadata_segment.get_header()
        # TODO : Change the number below
        header["seq"] = 2
        header["ack"] = 0
        metadata_segment.set_header(header)
        self.segment_list.append(metadata_segment)


        num_of_segment = self.get_segment_count()
        offset = 0
        for i in range(num_of_segment):
            segment = Segment()

            # Create payload
            offset += PAYLOAD_SIZE
            self.file.seek(offset)
            data_to_set = self.file.read(PAYLOAD_SIZE)
            segment.set_payload(data_to_set)

            # Create header
            header = segment.get_header()
            # TODO : Change the number below
            header["seq"] = i + 3
            header["ack"] = 3
            segment.set_header(header)
            self.segment_list.append(segment)

    def get_segment_count(self):
        """Get how many segment has to be created to sent the given file"""
        return ceil(self.get_file_size() / SEGMENT_SIZE)


if __name__ == "__main__":
    SERVER = Server()
    SERVER.listen_for_clients()
