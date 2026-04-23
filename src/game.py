from src.board import Board
import numpy as np

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = 1 
        self.phase = 'drop'
        self.pieces_dropped = 0
        
    def get_valid_moves(self):
        valid_moves = []
        if self.phase == 'drop':
            cells = np.argwhere(self.board.grid == 0)
            valid_moves = [('drop', r, c) for r, c in cells]
        else:
            for r, c in np.argwhere(self.board.grid == self.current_player):
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and self.board.grid[nr, nc] == 0:
                            valid_moves.append(('move', r, c, nr, nc))
        return valid_moves

    def make_move(self, move):
        # Safety check: ensures the move is legal before applying
        if move not in self.get_valid_moves():
            raise ValueError(f"Illegal move attempted: {move}")

        if move[0] == 'drop':
            self.board.grid[move[1], move[2]] = self.current_player
            self.pieces_dropped += 1
            if self.pieces_dropped == 8: self.phase = 'move'
        else:
            self.board.grid[move[1], move[2]] = 0
            self.board.grid[move[3], move[4]] = self.current_player
        
        self.current_player *= -1
    
    def check_game_over(self):
        return self.board.get_winner()