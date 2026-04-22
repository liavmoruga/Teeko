from src.player import RandomPlayer
from src.tournament import Tournament

# Create two random players
p1 = RandomPlayer(1)
p2 = RandomPlayer(-1)

# Initialize a tournament with 10,000 games
tourney = Tournament(p1, p2, num_games=100)

# Run the tournament AND save the dataset
tourney.play(save_dataset=False)