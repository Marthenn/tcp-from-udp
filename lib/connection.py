import socket
import threading

TIMEOUT = 5
SEGMENT_SIZE = 32768

class Connection() :
    def __init__(self, ip : str, port : int, broadcast : int, as_server : bool) -> None:
        self.ip = ip
        self.port = port
        self.broadcast_port = broadcast
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (as_server) :
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ip, broadcast))
            print("Server started on address", ip, "with port", broadcast)
        else :
            self.socket.bind(port)
            print("Client started on address", ip, "with port", port)
        self.socket.settimeout(TIMEOUT)
    
    def send(self, msg, ip : str, port : int) :
        self.socket.sendto(msg, (ip, port))
    
    def close(self) :
        self.socket.close()
    
    def listen_segment(self) :
        try :
            segment = self.socket.recv(SEGMENT_SIZE)
            return segment
        except TimeoutError :
            raise TimeoutError
    
    
