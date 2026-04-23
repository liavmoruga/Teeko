import numpy as np

class Board:
    def __init__(self):
        self.grid = np.zeros((5, 5), dtype=int)
        
    def get_canonical_state(self):
        best_state = None
        for k in range(4):
            rotated = np.rot90(self.grid, k)
            state = tuple(rotated.flatten())
            if best_state is None or state < best_state:
                best_state = state
            flipped = np.fliplr(rotated)
            state_flipped = tuple(flipped.flatten())
            if state_flipped < best_state:
                best_state = state_flipped
        return best_state

    def get_winner(self):
        """Returns the winner (1 or -1) if exists, else 0."""
        for player in [1, -1]:
            if self.check_win(player):
                return player
        return 0

    def check_win(self, player):
        # 1. Rows and Columns
        for i in range(5):
            for j in range(2): 
                if np.all(self.grid[i, j:j+4] == player) or np.all(self.grid[j:j+4, i] == player):
                    return True
        # 2. Diagonals
        for i in range(2):
            for j in range(2):
                if np.all([self.grid[i+k, j+k] == player for k in range(4)]) or \
                   np.all([self.grid[i+k, j+3-k] == player for k in range(4)]):
                    return True
        # 3. 2x2 Square
        for i in range(4):
            for j in range(4):
                if np.all(self.grid[i:i+2, j:j+2] == player):
                    return True
        return False