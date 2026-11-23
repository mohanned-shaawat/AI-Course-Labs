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
        self.isFinal = False # True when the utility is optimal not estimation
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

class GameSolver:
    
    def __init__(self, agent_is_first, max_depth):
        self.current_state = GameState()
        self.max_depth = max_depth
        if agent_is_first:
            self.agent_symbol = PLAYER1_SYMBOL
            self.is_agent_turn = True
        else:
            self.agent_symbol = PLAYER2_SYMBOL
            self.is_agent_turn = False
        self.expanded_nodes = 0
        self.total_expanded_nodes = 0

    def agent_move(self):
        if self.current_state.depth == GAME_LENGTH:
            raise Exception("Error: The game is already finished, no more moves can be played")
        if not self.is_agent_turn:
            raise Exception("Error: The agent caonnot move in the user's turn")
        move, self.current_state = self.max_move(self.current_state, self.max_depth)
        self.is_agent_turn = False
        return move, self.current_state

    def player_move(self, move):
        if self.current_state.depth == GAME_LENGTH:
            raise Exception("Error: The game is already finished, no more moves can be played")
        if self.is_agent_turn:
            raise Exception("Error: The user caonnot move in the agent's turn")
        if move not in self.current_state.generate_next_moves():
            return None
        self.expanded_nodes = 0
        self.current_state = self.current_state.generate_next_moves()[move]
        self.is_agent_turn = True
        return self.current_state

    def max_move(self, state, max_depth, alpha=-inf, beta=inf):
        pass

    def min_move(self, state, max_depth, alpha=-inf, beta=inf):
        pass

    def agent_fours(self, state=None):
        if state is None:
            return self.agent_fours(self.current_state)
        pass

    def user_fours(self, state=None):
        if state is None:
            return self.user_fours(self.current_state)
        pass

    def evaluate(self, state):
        return self.agent_fours(state) - self.user_fours(state)

    def estimate(self, state):
        pass

    def available_moves(self):
        return self.current_state.generate_next_moves().keys()
    
    def is_finished(self):
        return self.current_state.depth == GAME_LENGTH

    


