"""
The module for the server class of the file transfer application using UDP
"""
import sys
import os
import time
from typing import List
from math import ceil
from socket import timeout
from lib.parserGame import parse_args_game
from lib.connection import Connection
from lib.segment import Segment
from lib.constants import DEFAULT_IP, SEGMENT_SIZE, PAYLOAD_SIZE, SYN_FLAG, SYN_ACK_FLAG, ACK_FLAG, TIMEOUT_LISTEN, FIN_ACK_FLAG
from lib.tictactoe import TicTacToe
from lib.crc16 import crc16

class ServerGame:
    """
    The server class of the file transfer application using UDP
    The server should be able to:
    1. Establishes a three-way handshake connection with the server
    2. Send the file to the client
    """
    def __init__(self) -> None:
        args = parse_args_game(True)
        broadcast_port = args    
        self.conn = Connection(broadcast=broadcast_port, as_server=True)
        self.segment = Segment()
        self.segment_list : List[Segment] = []
        self.client_list = []
        self.tic_tac_toe = TicTacToe()

    def listen_for_clients(self) :
        print("[ INFO ] Listening for clients")
        while True:
            try :
                segment, client_addr = self.conn.listen_segment()
                client_ip, client_port = client_addr
                self.client_list.append(client_addr)
                print(f"[ INFO ] Received connection request from client: {client_ip}:{client_port}")

                answer = input("[ PROMPT ] Do you want to add more clients? (y/n) ")
                while not (answer.lower() in ["y", "n"]):
                    print("[ ERROR ] Invalid input")
                    answer = input("[ PROMPT ] Do you want to add more clients? (y/n) ")
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

    def initiate_transfer(self):
        for client in self.client_list:
            self.three_way_handshake(client)

    def start_game(self) :
        '''
        Mulai permainan sebagai pemain pertama (X)
        '''
        maxIdx = len(self.client_list)
        for idx, client in enumerate(self.client_list):
            print(f"[ INFO ] {idx+1}. {client[0]}:{client[1]}")
        chosenClient = int(input("Choose a client to play with. Type the number of the client from the list."))
        choiceValid = chosenClient <= maxIdx and chosenClient > 0
        while(not(choiceValid)) :
            chosenClient = int(input("Client number not valid. Type the number of the client from the list."))
            choiceValid = chosenClient <= maxIdx and chosenClient > 0

        while True :
            self.tic_tac_toe.board = self.tic_tac_toe.create_board()
            currClient = self.client_list[chosenClient-1]
            print("Client valid. Starting game as player X. Gets first turn.")
            gameOver = self.tic_tac_toe.check_game_over()
            while(not(gameOver)) :
                self.tic_tac_toe.print_board()
                selfMove = input("Where do you want to place your piece ? Type the number of one of the empty squares.")
                isValidMove = self.tic_tac_toe.play(int(selfMove))
                while (not(isValidMove)) :
                    selfMove = input("Square is not valid. Type the number of one of the empty squares.")
                    isValidMove = self.tic_tac_toe.play(int(selfMove))
                self.send_move(int(selfMove), currClient)
                gameOver = self.tic_tac_toe.check_game_over()
                if (gameOver) :
                    break
                oppMove = self.receive_move(currClient)
                print(oppMove)
                self.tic_tac_toe.play(oppMove)
                gameOver = self.tic_tac_toe.check_game_over()

            self.tic_tac_toe.print_board()
            print("The winner is", self.tic_tac_toe.get_winner())

            self.segment.set_flag([])
            self.close_connection(currClient)
            break
    
    def shutdown(self) :
        """Shutdown the server"""
        self.conn.close()

    def close_connection(self, client) :
        self.segment.set_flag([])
        fin_acked = False
        time_limit = time.time() + TIMEOUT_LISTEN

        while not fin_acked:
            try :
                self.segment.set_payload(bytes())
                self.segment.set_flag(["FIN", "ACK"])
                self.conn.send(self.segment.to_bytes(), client[0], client[1])
                response, client_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(response)
                if (client_addr == client and self.segment.get_flag() == ACK_FLAG) :
                    print(f'[Client {client[0]}:{client[1]}] Received ACK for FIN from client')
                    fin_acked = True
                elif (client_addr != client) :
                    print(f'[Client {client[0]}:{client[1]}] Received message from wrong client')
                else :
                    print(f'[Client {client[0]}:{client[1]}] Received non-ACK flag')
            except :
                if time.time() > time_limit:
                    print(
                        f"[ WARNING ] [Client {client[0]}:{client[1]}] [Timeout] Server waited too long, connection closed."
                    )
                    break
                print(f'[Client {client[0]}:{client[1]}] Connection timed out. Resending FIN message')
        
        client_fin_acked = False
        time_limit = time.time() + TIMEOUT_LISTEN
        while (not client_fin_acked) :
            try :
                response, client_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(response)
                if (client_addr == client and self.segment.get_flag() == FIN_ACK_FLAG) :
                    print(f'[Client {client[0]}:{client[1]}] Received FIN request from client. Sending ACK and shutting down connection.')
                    self.segment.set_payload(bytes())
                    self.segment.set_flag(["ACK"])
                    self.conn.send(self.segment.to_bytes(), client[0], client[1])
                    client_fin_acked = True
                elif (client_addr != client) :
                    print(f'[Client {client[0]}:{client[1]}] Received message from wrong client')
                else :
                    print(f'[Client {client[0]}:{client[1]}] Received non-FIN-ACK flag')
            except TimeoutError :
                if time.time() > time_limit:
                    print(
                        f"[ WARNING ] [Client {client[0]}:{client[1]}] [Timeout] Server waited too long, connection closed."
                    )
                    break
                print(f'[Client {client[0]}:{client[1]}] Connection timed out. Waiting again.')

    def send_move(self, move : int, currClient) :
        header = self.segment.get_header()
        header["seq"] = 0
        header["ack"] = 0
        self.segment.set_header(header)
        message = int.to_bytes(move,64,'big')
        self.segment.set_payload(message)
        self.segment.set_checksum(crc16(message))
        self.conn.send(self.segment.to_bytes(), currClient[0], currClient[1])

        moveAcked = False # Menentukan apakah gerakan sudah diterima server atau belum
        while(not(moveAcked)) :
            try :
                print("Before server send")
                data, client_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(data)
                print("After server send")
                if client_addr == currClient and self.segment.get_flag() == ACK_FLAG  :
                    print("Move successfully sent to client")
                    self.segment.set_flag([])
                    moveAcked = True
                else :
                    print("Received message from wrong address, listening again")
            except :
                print("Error sending move, sending again")
                header = self.segment.get_header()
                header["seq"] = 0
                header["ack"] = 0
                self.segment.set_header(header)
                self.segment.set_payload(message)
                self.segment.set_checksum(crc16(message))
                self.conn.send(self.segment.to_bytes(), currClient[0], currClient[1])
    
    def receive_move(self, currClient) :
        moveReceived = False
        while(not(moveReceived)) :
            try :
                data, server_addr = self.conn.listen_segment()
                self.segment = Segment.from_bytes(data)
                if server_addr == currClient  :
                    if self.segment.is_valid() :
                        print("Move successfully received from client")
                        moveReceived = True
                        oppMove = int.from_bytes(self.segment.get_payload(), "big")
                        header = self.segment.get_header()
                        header["ack"] = header["seq"] + 1
                        header["seq"] = 0
                        self.segment.set_header(header)
                        self.segment.set_payload(bytes())
                        self.segment.set_flag(["ACK"])
                        self.conn.send(self.segment.to_bytes(), currClient[0], currClient[1])
                        return(oppMove)
                    else :
                        print("Received message is corrupted, listening again")
                else :
                    print("Received message from wrong address, listening again")
            except :
                print("Error receiving move, waiting again")

if __name__ == "__main__":
    SERVER = ServerGame()
    SERVER.listen_for_clients()
    SERVER.initiate_transfer()
    SERVER.start_game()