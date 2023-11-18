import socket

class Connection() :
    def __init__(self, ip : str, port : int, broadcast : int, as_server : bool) -> None:
        self.ip = ip
        self.port = port
        self.broadcast_port = broadcast
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (as_server) :
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        print("Connection open")
    
    def send(self, msg, ip : str, port : int) :
        self.socket.sendto(msg, (ip, port))
    
    def close(self) :
        self.socket.close()
    
    def listen(self) :
        while True :
            print("Waiting for client") 
            msg, address = self.socket.recvfrom(2048)
            print("Received message:",  msg, "from", address)
