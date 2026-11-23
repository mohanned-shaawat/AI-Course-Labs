from math import inf


BOARD_WIDTH = 7
BOARD_HIGHT = 6
GAME_LENGTH = BOARD_WIDTH * BOARD_HIGHT

PLAYER1_SYMBOL = "X"
PLAYER2_SYMBOL = "O"
EMPTY_SYMBOL = " "



class GameState:
    def __init__(self, board=None, top=None, depth=0):
        self.depth = depth
        if board is None:
            self.board = [[EMPTY_SYMBOL] * BOARD_WIDTH for _ in range(BOARD_HIGHT)]
        else:
            self.board = board
        if top is None:
            self.top = [BOARD_HIGHT - 1] * BOARD_WIDTH
        else:
            self.top = top
        self.utility = None
        self.isFinal = False
        self.next_moves = None
        self.pruned = False

    def generate_next_moves(self):
        if self.next_moves is not None:
            return self.next_moves
        moves = {}
        symbol = PLAYER1_SYMBOL if self.depth % 2 == 0 else PLAYER2_SYMBOL
        for i in range(BOARD_WIDTH):
            if self.top[i] >= 0:
                new_board = [self.board[j][:] for j in range(BOARD_HIGHT)]
                new_board[self.top[i]][i] = symbol
                new_top = self.top[:]
                new_top[i] -= 1
                moves[i + 1] = GameState(new_board, new_top, self.depth + 1)
        
        self.next_moves = moves
        return moves


def select_move(state, max_depth):
    if state.depth % 2 == 0:
        return max_move(state, max_depth)
    else:
        return min_move(state, max_depth)

def max_move(state, max_depth, alpha=-inf, beta=inf):
    pass

def min_move(state, max_depth, alpha=-inf, beta=inf):
    pass

def evaluate(state):
    pass

def estimate(state):
    pass


