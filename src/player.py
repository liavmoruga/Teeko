import random
import numpy as np
import copy
import os

class Player:
    """Base class for all AI and Human players."""
    def get_move(self, game):
        raise NotImplementedError("Players must implement the get_move method.")

class RandomPlayer(Player):
    """An AI that makes completely random legal moves."""
    def get_move(self, game):
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        return random.choice(valid_moves)

class SmartPlayer(Player):
    """An AI that uses a Keras Neural Network to evaluate and choose the best moves."""
    def __init__(self, model_path, player_id):
        # Suppress TensorFlow startup logs to keep the terminal clean
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
        import tensorflow as tf
        
        self.model = tf.keras.models.load_model(model_path)
        self.player_id = player_id # 1 for Player 1, -1 for Player 2
        
    def get_move(self, game):
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
            
        # Optimization: Batch process all potential future states
        states_batch = []
        
        for move in valid_moves:
            # 1. Simulate the move on a copy of the game
            game_copy = copy.deepcopy(game)
            game_copy.make_move(move)
            
            # 2. Extract the resulting board state and whose turn is next
            state_tuple = game_copy.board.get_canonical_state()
            turn = game_copy.current_player
            
            # 3. Add to our batch
            states_batch.append(list(state_tuple) + [turn])
            
        # Convert to numpy array (Shape: [Number of valid moves, 26])
        input_data = np.array(states_batch)
        
        # 4. Predict the value of all states in one massive calculation
        # The model predicts the probability of Player 1 winning (0.0 to 1.0)
        predictions = self.model.predict(input_data, verbose=0).flatten()
        
        # 5. Choose the best move based on who this AI is playing as
        if self.player_id == 1:
            # Player 1 wants to MAXIMIZE the score
            best_idx = np.argmax(predictions)
        else:
            # Player 2 wants to MINIMIZE Player 1's score (which means maximizing their own)
            best_idx = np.argmin(predictions)
            
        return valid_moves[best_idx]
