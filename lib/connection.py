import socket
from constants import TIMEOUT, SEGMENT_SIZE, DEFAULT_IP, DEFAULT_BROADCAST_PORT, DEFAULT_PORT


class Connection() :
    """Class representing the socket connection"""
    def __init__(self, ip : str = DEFAULT_IP, port : int = DEFAULT_PORT, broadcast : int = DEFAULT_BROADCAST_PORT, as_server : bool = False) -> None:
        self.ip = ip
        self.port = port
        self.broadcast_port = broadcast
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (as_server) :
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ip, broadcast))
            print("Server started on address", ip, "with port", broadcast)
        else :
            self.socket.bind((ip, port))
            print("Client started on address", ip, "with port", port)
        self.socket.settimeout(TIMEOUT)
    
    def send(self, msg, ip : str, port : int) :
        """Send message through given ip and port"""
        self.socket.sendto(msg, (ip, port))
    
    def close(self) :
        """Close the socket held by the Connection object"""
        self.socket.close()
    
    def listen_segment(self) :
        """Listen for segment from the socket held by this object"""
        try :
            segment = self.socket.recv(SEGMENT_SIZE)
            return segment
        except TimeoutError as exc:
            raise TimeoutError from exc
        