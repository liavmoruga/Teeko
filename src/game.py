import numpy as np
from src.board import Board

class Game:
    """Manages the flow, turns, and phase transitions of a Teeko game."""
    
    def __init__(self):
        self.board = Board()
        self.current_player = 1 
        self.phase = 'drop'
        self.pieces_dropped = 0
        
    def get_valid_moves(self):
        """Returns a list of all legal moves for the current player based on the phase."""
        valid_moves = []
        
        if self.phase == 'drop':
            cells = np.argwhere(self.board.grid == 0)
            valid_moves = [('drop', r, c) for r, c in cells]
        else:
            for r, c in np.argwhere(self.board.grid == self.current_player):
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and self.board.grid[nr, nc] == 0:
                            valid_moves.append(('move', r, c, nr, nc))
        return valid_moves

    def make_move(self, move):
        """Applies a move. Raises an error if the move is illegal."""
        if move not in self.get_valid_moves():
            raise ValueError(f"Illegal move attempted by Player {self.current_player}: {move}")

        if move[0] == 'drop':
            self.board.grid[move[1], move[2]] = self.current_player
            self.pieces_dropped += 1
            if self.pieces_dropped == 8: 
                self.phase = 'move'
        elif move[0] == 'move':
            self.board.grid[move[1], move[2]] = 0
            self.board.grid[move[3], move[4]] = self.current_player
        
        # Swap turn
        self.current_player *= -1
    
    def check_game_over(self):
        """Checks if the game has concluded."""
        return self.board.get_winner()