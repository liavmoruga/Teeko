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

class TerminalPlayer(Player):
    """A human player that inputs moves via the terminal with robust validation."""
    def get_move(self, game):
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
            
        print(f"\n--- Player {game.current_player}'s Turn ---")
        print(f"Phase: {game.phase.upper()}")
        
        while True:
            try:
                if game.phase == 'drop':
                    print("Enter coordinates to DROP a piece (row col), e.g., '2 2': ")
                    user_input = input(">> ").strip().split()
                    
                    if len(user_input) != 2:
                        print("❌ Invalid input. Please enter exactly two numbers.")
                        continue
                        
                    r, c = int(user_input[0]), int(user_input[1])
                    move = ('drop', r, c)
                    
                else:
                    print("Enter coordinates to MOVE (from_row from_col to_row to_col), e.g., '2 2 3 3': ")
                    user_input = input(">> ").strip().split()
                    
                    if len(user_input) != 4:
                        print("❌ Invalid input. Please enter exactly four numbers.")
                        continue
                        
                    r1, c1, r2, c2 = int(user_input[0]), int(user_input[1]), int(user_input[2]), int(user_input[3])
                    move = ('move', r1, c1, r2, c2)
                    
                if move in valid_moves:
                    return move
                else:
                    print("❌ Illegal move! The cell might be taken, out of bounds, or not adjacent.")
                    
            except ValueError:
                print("❌ Invalid format! Please use numbers only.")

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





















class MinimaxPlayer(Player):
    """
    An elite AI that uses Minimax with Alpha-Beta pruning, Root Move Ordering,
    and a Batch Prediction engine to drastically speed up calculation times.
    """
    def __init__(self, model_path, player_id, depth=3): # Notice depth=3 is now feasible!
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
        import tensorflow as tf
        
        self.model = tf.keras.models.load_model(model_path)
        self.player_id = player_id
        self.depth = depth
        self.prediction_cache = {}

    def get_move(self, game):
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
            
        # --- 1. ROOT MOVE ORDERING ---
        states_batch = []
        for move in valid_moves:
            game_copy = copy.deepcopy(game)
            game_copy.make_move(move)
            states_batch.append(list(game_copy.board.get_canonical_state()) + [game_copy.current_player])
            
        input_data = np.array(states_batch)
        predictions = self.model.predict(input_data, verbose=0).flatten()
        
        sorted_indices = np.argsort(predictions)
        if self.player_id == 1:
            sorted_indices = sorted_indices[::-1]
            
        ordered_moves = [valid_moves[i] for i in sorted_indices]
        self.prediction_cache = {}

        # --- 2. ALPHA-BETA SEARCH WITH TIE-BREAKING ---
        best_moves = []
        is_maximizing = (self.player_id == 1)
        
        # Bug Fix: Initialize alpha-beta bounds at the root
        alpha = -float('inf')
        beta = float('inf')
        
        if is_maximizing:
            best_val = -float('inf')
            for move in ordered_moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                val = self._minimax(game_copy, self.depth - 1, alpha, beta, False)
                
                # Tie-breaking logic: Collect all equally good moves
                if val > best_val:
                    best_val = val
                    best_moves = [move]
                elif val == best_val:
                    best_moves.append(move)
                    
                alpha = max(alpha, best_val)
        else:
            best_val = float('inf')
            for move in ordered_moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                val = self._minimax(game_copy, self.depth - 1, alpha, beta, True)
                
                if val < best_val:
                    best_val = val
                    best_moves = [move]
                elif val == best_val:
                    best_moves.append(move)
                    
                beta = min(beta, best_val)
                
        # Return a random move from the absolute best options to avoid loops
        return random.choice(best_moves) if best_moves else ordered_moves[0]

    def _minimax(self, game, depth, alpha, beta, is_maximizing):
        winner = game.check_game_over()
        if winner == 1: return 1.0  
        if winner == -1: return 0.0 
        
        valid_moves = game.get_valid_moves()
        if not valid_moves: return 0.5 
        
        # --- 3. THE MASSIVE OPTIMIZATION: BATCH EVALUATION AT DEPTH 1 ---
        # Instead of recursing to depth 0 and predicting 1 by 1, we predict all leaves at once.
        if depth == 1:
            best_val = -float('inf') if is_maximizing else float('inf')
            states_batch = []
            cache_keys = []
            
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                
                w = game_copy.check_game_over()
                if w != 0:
                    states_batch.append("TERMINAL")
                    cache_keys.append(1.0 if w == 1 else 0.0)
                    continue
                    
                state_tuple = game_copy.board.get_canonical_state()
                turn = game_copy.current_player
                cache_key = (state_tuple, turn)
                
                if cache_key in self.prediction_cache:
                    states_batch.append("CACHED")
                    cache_keys.append(self.prediction_cache[cache_key])
                else:
                    states_batch.append(list(state_tuple) + [turn])
                    cache_keys.append(cache_key)
                    
            # Predict only the uncached, non-terminal states in one fast batch
            needs_prediction = [s for s in states_batch if isinstance(s, list)]
            if needs_prediction:
                predictions = self.model.predict(np.array(needs_prediction), verbose=0).flatten()
                pred_idx = 0
                
            # Simulate the alpha-beta check conceptually on the collected data
            for i in range(len(states_batch)):
                if states_batch[i] in ["TERMINAL", "CACHED"]:
                    val = cache_keys[i]
                else:
                    val = float(predictions[pred_idx])
                    self.prediction_cache[cache_keys[i]] = val
                    pred_idx += 1
                    
                if is_maximizing:
                    best_val = max(best_val, val)
                    alpha = max(alpha, best_val)
                else:
                    best_val = min(best_val, val)
                    beta = min(beta, best_val)
                    
                if beta <= alpha:
                    break # Prune!
                    
            return best_val

        # Fallback for depth == 0 (Should only trigger if you initialize with depth=1)
        if depth == 0:
            state_tuple = game.board.get_canonical_state()
            turn = game.current_player
            cache_key = (state_tuple, turn)
            if cache_key in self.prediction_cache: return self.prediction_cache[cache_key]
            prediction = self.model.predict(np.array([list(state_tuple) + [turn]]), verbose=0)[0][0]
            self.prediction_cache[cache_key] = prediction
            return prediction

        # --- 4. STANDARD RECURSION FOR DEPTH > 1 ---
        if is_maximizing:
            max_eval = -float('inf')
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                
                eval_score = self._minimax(game_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha: break
            return max_eval
            
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                
                eval_score = self._minimax(game_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha: break
            return min_eval