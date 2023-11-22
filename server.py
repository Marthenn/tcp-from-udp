from .lib.parser import parse_args
from .lib.connection import Connection
from .lib.segment import Segment
from .lib.constants import DEFAULT_BROADCAST_PORT, DEFAULT_IP, DEFAULT_PORT
import os 

class Server :
    def __init__(self) -> None:
        args = parse_args(True)
        broadcast_port, path_file = args
        self.conn = Connection(broadcast=broadcast_port, as_server=True)
        self.file_path = path_file
        self.file = self.open_file()
        self.segment = Segment()
    
    def three_way_handshake(self, client_ip : str, client_port : int) -> bool :
        print ("Initiating handshake with client :", client_ip, client_port)

    def open_file(self) :
        return open(self.file_path)
    
    def get_file_size(self) :
        try :
            return os.path.getsize(self.file_path)
        except :
            print("Error reading file", self.file_path, ". Aborting.")

    def three_way_handshake(self, client:tuple(str,int)) :
        self.segment.set_flag(["SYN"])
        