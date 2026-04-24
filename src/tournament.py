import csv
from src.game import Game

class Tournament:
    """Manages game simulations on a single thread for simplicity and debugging."""
    def __init__(self, player1, player2, num_games=100):
        self.player1 = player1
        self.player2 = player2
        self.num_games = num_games
        self.dataset = []
        
        # Statistics tracking
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0

    def play(self, save_dataset=False, filename="dataset.csv", max_moves=100, moves_before_finish=20, gamma=0.9, min_diff=0.05, save_draws=False):
        """Runs the tournament sequentially."""
        print(f"Starting Tournament: {self.num_games} games...")
        
        for i in range(self.num_games):
            self.print_progress_bar(i, self.num_games)
            
            game = Game()
            players = {1: self.player1, -1: self.player2}
            current_game_states = []
            moves_count = 0
            winner = 0
            
            # Game loop
            while moves_count < max_moves and winner == 0:
                current_p = players[game.current_player]
                move = current_p.get_move(game)
                
                if not move: 
                    break

                if save_dataset:
                    # Save the canonical state exactly when the move is made
                    state = game.board.get_canonical_state()
                    current_game_states.append((state, game.current_player))
                    
                game.make_move(move)
                winner = game.check_game_over()
                moves_count += 1

            # Update stats
            if winner == 1: 
                self.player1_wins += 1
            elif winner == -1: 
                self.player2_wins += 1
            else: 
                self.draws += 1
                
            # Process data if required
            if save_dataset and (winner != 0 or save_draws):
                self._extract_game_data(current_game_states, winner, moves_before_finish, gamma, min_diff)
                    
        self.print_progress_bar(self.num_games, self.num_games)
        print("\nTournament finished!")
        self.print_results()
        
        if save_dataset:
            self.save_to_csv(filename)

    def _extract_game_data(self, game_states, winner, moves_before_finish, gamma, min_diff):
        """Internal helper to process and label game states."""
        total_moves = len(game_states)
        start_idx = max(0, total_moves - moves_before_finish)
        
        for idx in range(start_idx, total_moves):
            state_tuple, turn = game_states[idx]
            distance_from_end = total_moves - 1 - idx
            
            # Label calculation
            if winner == 0:
                decayed_label = 0.5
            else:
                decayed_label = 0.5 + (0.5 * winner * (gamma ** distance_from_end))
            
            final_label = round(decayed_label, 4)

            # Noise filter
            if winner == 0 or abs(final_label - 0.5) > min_diff:
                self.dataset.append(list(state_tuple) + [turn, final_label])

    def print_progress_bar(self, iteration, total, length=50):
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = '█' * filled_length + '-' * (length - filled_length)
        print(f'\rProgress: |{bar}| {percent}% Complete [{iteration}/{total}]', end='\r')
        if iteration == total: print()

    def print_results(self):
        print("-" * 35)
        print(f"P1 Wins: {self.player1_wins} | P2 Wins: {self.player2_wins} | Draws: {self.draws}")
        print("-" * 35)

    def save_to_csv(self, filename):
        if not self.dataset:
            print("No data collected.")
            return
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f'pos_{i}' for i in range(25)] + ['turn', 'label'])
            writer.writerows(self.dataset)
        print(f"Dataset securely saved with {len(self.dataset)} samples.")