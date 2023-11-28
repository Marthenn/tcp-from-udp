"""
The module for the client class of the file transfer application using UDP
"""
import sys
from socket import timeout
from lib.parserGame import parse_args_game
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import ACK_FLAG, SYN_ACK_FLAG, SYN_FLAG, DEFAULT_IP
from lib.crc16 import crc16
from lib.tictactoe import TicTacToe

class ClientGame:
    """
    The client class of the tic-tac-toe game application using UDP
    The client should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Send and receive moves from the opponent
    3. Sends the acknowledgement to the server
    """

    def __init__(self):
        client_port, broadcast_port = parse_args_game(False)
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.conn = Connection(
            port=self.client_port, broadcast=self.broadcast_port, as_server=False
        )
        self.segment = Segment()
        self.tic_tac_toe = TicTacToe()

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

    def start_game(self) :
        '''
        Mulai permainan sebagai pemain kedua (O)
        '''
        print("Starting game as player O. Gets second turn.")
        gameOver = self.tic_tac_toe.check_game_over()
        while(not(gameOver)) :
            oppMove = self.receive_move()
            print(oppMove)
            self.tic_tac_toe.play(oppMove)
            self.tic_tac_toe.print_board()
            gameOver = self.tic_tac_toe.check_game_over()
            if(gameOver) :
                break

            selfMove = input("Where do you want to place your piece ? Type the number of one of the empty squares.")
            isValidMove = self.tic_tac_toe.play(int(selfMove))
            while (not(isValidMove)) :
                selfMove = input("Square is not valid. Type the number of one of the empty squares.")
                isValidMove = self.tic_tac_toe.play(int(selfMove))
            self.send_move(int(selfMove))
            gameOver = self.tic_tac_toe.check_game_over()
        print("The winner is", self.tic_tac_toe.get_winner())

    def send_move(self, move : int) :
        message = int.to_bytes(move,64,'big')
        self.segment.set_flag([])
        self.segment.set_payload(message)
        self.segment.set_checksum(crc16(message))
        self.conn.send(self.segment.to_bytes(), self.conn.ip, self.broadcast_port)

        moveAcked = False # Menentukan apakah gerakan sudah diterima server atau belum
        while(not(moveAcked)) :
            # try :
                data, server_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(data)
                if server_addr == (DEFAULT_IP, self.broadcast_port) and self.segment.get_flag() == ACK_FLAG  :
                    print("Move successfully sent to server")
                    self.segment.set_flag([])
                    moveAcked = True
                else :
                    print("Received message from wrong address, listening again")
            # except :
                print("Error sending move, sending again")
                self.segment.set_payload(message)
                self.segment.set_checksum(crc16(message))
                self.conn.send(self.segment.to_bytes(), self.conn.ip, self.broadcast_port)
    
    def receive_move(self) :
        moveReceived = False
        while(not(moveReceived)) :
            # try :
                print("Before listen")
                data, server_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(data)
                print("After listen")
                if server_addr == (DEFAULT_IP, self.broadcast_port)  :
                    if self.segment.is_valid() :
                        print("Move successfully received from server")
                        moveReceived = True
                        oppMove = int.from_bytes(self.segment.get_payload(), "big")
                        self.segment.set_payload(bytes())
                        self.segment.set_flag(["ACK"])
                        self.conn.send(self.segment.to_bytes(), self.conn.ip, self.broadcast_port)
                        return(oppMove)
                    else :
                        print("Received message is corrupted, listening again")
                else :
                    print("Received message from wrong address, listening again")
            # except :
            #     print("Error receiving move, waiting again")

if __name__ == "__main__":
    CLIENT = ClientGame()
    CLIENT.connect()
    CLIENT.three_way_handshake()
    CLIENT.start_game()
