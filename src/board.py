import numpy as np

class Board:
    def __init__(self):
        # Initialize a 5x5 board
        # 0 = Empty, 1 = Player 1, -1 = Player 2
        self.grid = np.zeros((5, 5), dtype=int)
        
    def get_canonical_state(self):
        # Generates all 8 symmetries (4 rotations + 4 reflections)
        # Returns the lexicographically smallest tuple representation
        # This normalizes the board state for the dataset and model training
        best_state = None
        
        for k in range(4):
            # Rotate board 90 degrees 'k' times
            rotated = np.rot90(self.grid, k)
            state = tuple(rotated.flatten())
            
            # Keep the smallest state found so far
            if best_state is None or state < best_state:
                best_state = state
                
            # Reflect the current rotated board (Horizontal flip)
            flipped = np.fliplr(rotated)
            state_flipped = tuple(flipped.flatten())
            
            # Check against the smallest state
            if state_flipped < best_state:
                best_state = state_flipped
                
        return best_state

    def check_win(self, player):
        # Standard Teeko win conditions: 4 in a row or a 2x2 square
        
        # 1. Check horizontal and vertical sequences (4 in a row)
        for i in range(5):
            for j in range(2): 
                # Horizontal check
                if np.all(self.grid[i, j:j+4] == player):
                    return True
                # Vertical check
                if np.all(self.grid[j:j+4, i] == player):
                    return True

        # 2. Check diagonal sequences (4 in a row)
        for i in range(2):
            for j in range(2):
                # Main diagonal direction check
                if np.all([self.grid[i+k, j+k] == player for k in range(4)]):
                    return True
                # Anti-diagonal direction check
                if np.all([self.grid[i+k, j+3-k] == player for k in range(4)]):
                    return True

        # 3. Check 2x2 square (Specific Teeko rule)
        for i in range(4):
            for j in range(4):
                if (self.grid[i, j] == player and self.grid[i+1, j] == player and
                    self.grid[i, j+1] == player and self.grid[i+1, j+1] == player):
                    return True

        return False

    def is_full(self):
        # Checks if there are no empty spaces left on the board
        return not np.any(self.grid == 0)

    def count_pieces(self, player):
        # Returns the number of pieces currently placed by a specific player
        return np.sum(self.grid == player)

    def print_board(self):
        # Terminal representation for debugging purposes
        symbols = {0: '.', 1: 'X', -1: 'O'}
        for row in self.grid:
            print(" ".join([symbols[val] for val in row]))
        print("-" * 15)