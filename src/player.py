from abc import ABC, abstractmethod
import random
import numpy as np
import copy

class Player(ABC):
    def __init__(self, symbol):
        self.symbol = symbol

    @abstractmethod
    def get_move(self, game_state):
        pass

class RandomPlayer(Player):
    def get_move(self, game_state):
        valid_moves = game_state.get_valid_moves()
        if valid_moves:
            return random.choice(valid_moves)
        return None

class SmartPlayer(Player):
    def __init__(self, symbol, model):
        super().__init__(symbol)
        self.model = model # The trained TensorFlow model

    def get_move(self, game_state):
        valid_moves = game_state.get_valid_moves()
        if not valid_moves:
            return None

        best_move = None
        best_score = -float('inf')

        # We evaluate every possible move
        for move in valid_moves:
            # 1. Create a deep copy of the game so we don't ruin the real match
            simulated_game = copy.deepcopy(game_state)
            
            # 2. Apply the move to the simulation
            simulated_game.make_move(move)
            
            # 3. Get the canonical state of the RESULTING board
            canonical_state = simulated_game.board.get_canonical_state()
            
            # 4. Format the state for TensorFlow (1D array shape: (1, 25))
            model_input = np.array(canonical_state).reshape(1, -1)
            
            # 5. Predict the win probability
            # The model outputs the probability of Player 1 winning.
            prediction = self.model.predict(model_input, verbose=0)[0][0]
            
            # 6. Adjust score based on who the SmartPlayer is playing as.
            # If the AI is Player 1 (1), it wants high predictions.
            # If the AI is Player 2 (-1), it wants low predictions (closer to 0), 
            # so we invert the score to maximize it.
            score = prediction if self.symbol == 1 else (1 - prediction)
            
            # 7. Keep track of the move that leads to the best score
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
    

class TerminalPlayer(Player):
    def get_move(self, game_state):
        valid_moves = game_state.get_valid_moves()
        
        while True:
            # Indicate the current phase so the user knows what input is expected
            print(f"\nPlayer {self.symbol}'s turn. Phase: {game_state.phase.upper()}")
            
            try:
                if game_state.phase == 'drop':
                    user_input = input("Enter drop coords (row col) e.g., '2 3': ")
                    r, c = map(int, user_input.split())
                    move = ('drop', r, c)
                else:
                    user_input = input("Enter move coords (r1 c1 r2 c2) e.g., '2 3 3 4': ")
                    r1, c1, r2, c2 = map(int, user_input.split())
                    move = ('move', r1, c1, r2, c2)
                    
                # Validate the parsed move against the engine's legal moves
                if move in valid_moves:
                    return move
                else:
                    print("ERROR: Invalid move. It might be occupied or against the rules. Try again.")
                    
            except ValueError:
                # Catch cases where the user typed letters or wrong number of coordinates
                print("ERROR: Invalid format. Please use integers separated by spaces.")