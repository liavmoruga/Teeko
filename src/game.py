import numpy as np
import random
from src.board import Board

class Game:
    def __init__(self, max_moves=200):
        self.board = Board()
        # Player 1 starts, represented by 1. Player 2 is represented by -1.
        self.current_player = 1 
        self.phase = 'drop' # The game starts in the drop phase
        self.pieces_dropped = 0 # Counter to track when to switch to move phase
        self.moves_played = 0
        self.max_moves = max_moves
        
    def get_valid_moves(self):
        # Returns a list of all valid moves for the current player based on the phase
        valid_moves = []
        
        if self.phase == 'drop':
            # Any empty spot is a valid move
            for i in range(5):
                for j in range(5):
                    if self.board.grid[i, j] == 0:
                        valid_moves.append(('drop', i, j))
        else:
            # Move phase: find current player's pieces and check adjacent empty spots
            for i in range(5):
                for j in range(5):
                    if self.board.grid[i, j] == self.current_player:
                        # Check all 8 directions
                        for di in [-1, 0, 1]:
                            for dj in [-1, 0, 1]:
                                if di == 0 and dj == 0:
                                    continue
                                
                                ni, nj = i + di, j + dj
                                # Check boundaries and if the spot is empty
                                if 0 <= ni < 5 and 0 <= nj < 5 and self.board.grid[ni, nj] == 0:
                                    valid_moves.append(('move', i, j, ni, nj))
        return valid_moves

    def make_move(self, move):
        # Applies a move to the board and updates game state
        action = move[0]
        
        if action == 'drop':
            _, r, c = move
            self.board.grid[r, c] = self.current_player
            self.pieces_dropped += 1
            # Switch to move phase after 8 pieces are placed (4 per player)
            if self.pieces_dropped == 8:
                self.phase = 'move'
                
        elif action == 'move':
            _, r1, c1, r2, c2 = move
            # Remove piece from original spot
            self.board.grid[r1, c1] = 0
            # Place piece in new spot
            self.board.grid[r2, c2] = self.current_player
        
        self.current_player *= -1
        self.moves_played += 1
    
    def check_game_over(self):
            # Check if the previous player won (since turns switch after a move)
            prev_player = self.current_player * -1
            
            if self.board.check_win(prev_player):
                return prev_player
                
            # Check for draw
            if self.moves_played >= self.max_moves:
                return 0
                
            # Game is still ongoing
            return None