from enum import Enum

class Player(Enum):
    X = 1
    O = 2

class TicTacToe:
    def __init__(self):
        self.board = self.create_board()
        self.turn = Player.X

    def create_board(self):
        board = {}
        for i in range(1, 10):
            board[i] = 0
        return board

    def print_board(self):
        for i in range(1, 10):
            if self.board[i] == 0:
                print(i, end=" ")
            elif self.board[i] == 1:
                print("X", end=" ")
            else:
                print("O", end=" ")
            if i % 3 == 0:
                print()

    def check_win(self):
        # Check horizontal
        for i in range(1, 10, 3):
            if self.board[i] == self.board[i+1] == self.board[i+2] != 0:
                return True

        # Check vertical
        for i in range(1, 4):
            if self.board[i] == self.board[i+3] == self.board[i+6] != 0:
                return True

        # Check diagonal
        if self.board[1] == self.board[5] == self.board[9] != 0:
            return True
        if self.board[3] == self.board[5] == self.board[7] != 0:
            return True

        return False

    def check_draw(self):
        for i in range(1, 10):
            if self.board[i] == 0:
                return False
        return True

    def check_game_over(self):
        if self.check_win():
            return True
        if self.check_draw():
            return True
        return False

    def get_winner(self):
        if self.check_win():
            if self.turn == Player.X:
                return Player.O
            else:
                return Player.X
        else:
            return None

    def play(self, pos):
        if pos >= 1 and pos < 10 and self.board[pos] == 0:
            if self.turn == Player.X:
                self.board[pos] = 1
                self.turn = Player.O
            else:
                self.board[pos] = 2
                self.turn = Player.X
            return True
        else:
            return False

if __name__ == '__main__':
    game = TicTacToe()
    game.print_board()
    while not game.check_game_over():
        pos = int(input("Input position: "))
        game.play(pos)
        game.print_board()
    print("Game over")
    print("Winner:", game.get_winner())
