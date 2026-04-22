import csv
from src.board import Board
from src.game import Game

class Tournament:
    def __init__(self, player1, player2, num_games=100):
        self.player1 = player1
        self.player2 = player2
        self.num_games = num_games
        self.dataset = []
        
        # Statistics tracking
        self.player1_wins = 0
        self.player2_wins = 0
        self.draws = 0

    def print_progress_bar(self, iteration, total, length=50):
        # Calculates the percentage and formats the bar string
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = '█' * filled_length + '-' * (length - filled_length)
        
        # \r brings the cursor back to the start of the line to overwrite it
        print(f'\rProgress: |{bar}| {percent}% Complete [{iteration}/{total}]', end='\r')
        
        # Print a new line on completion so the next print doesn't overwrite the bar
        if iteration == total:
            print()

    def play(self, save_dataset=False):
        print(f"Starting tournament: {self.num_games} games.")
        print(f"Player 1 ({type(self.player1).__name__}) VS Player 2 ({type(self.player2).__name__})")
        print(f"Saving dataset: {save_dataset}\n")
        
        for i in range(self.num_games):
            # Update the progress bar at the start of each game
            self.print_progress_bar(i, self.num_games)
            
            game = Game()
            players = {1: self.player1, -1: self.player2}
            
            current_game_states = []
            
            # Game loop
            while True:
                winner = game.check_game_over()
                
                if winner is not None:
                    break
                    
                current_p = players[game.current_player]
                move = current_p.get_move(game)
                
                if not move:
                    winner = 0 
                    break 
                    
                if save_dataset:
                    state = game.board.get_canonical_state()
                    # We MUST save whose turn it is alongside the board state
                    current_game_states.append((state, game.current_player))
                    
                game.make_move(move)
            
            # Update statistics based on the game outcome
            if winner == 1:
                self.player1_wins += 1
            elif winner == -1:
                self.player2_wins += 1
            else:
                self.draws += 1
                
            # Save data if enabled and there's a clear winner
            # Save data if enabled and there's a clear winner
            if save_dataset and winner != 0:
                label = 1 if winner == 1 else 0
                for state_tuple, turn in current_game_states:
                    # Convert tuple to list, add the turn, and add the label
                    row = list(state_tuple) + [turn, label]
                    self.dataset.append(row)
                    
        # Force the progress bar to show 100% when the loop finishes
        self.print_progress_bar(self.num_games, self.num_games)
        print("\nTournament finished!")
        
        # Print the final stats
        self.print_results()
        
        # Save to file if required
        if save_dataset:
            self.save_to_csv()

    def print_results(self):
        print("-" * 35)
        print("Tournament Results:")
        print(f"Player 1 Wins: {self.player1_wins} ({(self.player1_wins/self.num_games)*100:.1f}%)")
        print(f"Player 2 Wins: {self.player2_wins} ({(self.player2_wins/self.num_games)*100:.1f}%)")
        print(f"Draws:         {self.draws} ({(self.draws/self.num_games)*100:.1f}%)")
        print("-" * 35)

    def save_to_csv(self):
        filename = 'dataset.csv'
        if not self.dataset:
            print("No data to save.")
            return
            
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Create header row: 25 squares, 1 turn indicator, 1 label
            header = [f'pos_{i}' for i in range(25)] + ['turn', 'label']
            writer.writerow(header)
            writer.writerows(self.dataset)
            
        print(f"Dataset successfully saved to {filename}!")
        print(f"Total valid board states collected: {len(self.dataset)}")