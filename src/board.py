import numpy as np

class Board:
    """Handles the physical representation of the Teeko board and its rules."""
    
    def __init__(self):
        # 0 = Empty, 1 = Player 1, -1 = Player 2
        self.grid = np.zeros((5, 5), dtype=int)
        
    def get_canonical_state(self):
        """
        Normalizes the board state using 8 symmetries (4 rotations + 4 reflections).
        This reduces the state space the model has to learn by up to 8x.
        """
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
        """Returns the winning player (1 or -1), or 0 if no one has won."""
        for player in [1, -1]:
            if self._check_win_for_player(player):
                return player
        return 0

    def _check_win_for_player(self, player):
        """Internal method to check all Teeko win conditions for a specific player."""
        # 1. Rows and Columns (4 in a row)
        for i in range(5):
            for j in range(2): 
                if np.all(self.grid[i, j:j+4] == player) or np.all(self.grid[j:j+4, i] == player):
                    return True
                    
        # 2. Diagonals (4 in a row)
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
    
    def print_board(self):
        """Prints the board to the terminal for debugging and playing."""
        symbols = {1: 'X', -1: 'O', 0: '.'}
        print("  0 1 2 3 4")
        for i, row in enumerate(self.grid):
            print(f"{i} " + " ".join([symbols[val] for val in row]))
        print()