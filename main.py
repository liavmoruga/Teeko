from src.player import RandomPlayer
from src.tournament import Tournament

p1 = RandomPlayer(1)
p2 = RandomPlayer(-1)

t = Tournament(p1, p2, num_games=70000)
t.play(save_dataset=True, max_moves=80, moves_before_finish=20, gamma=0.88, min_diff=0.06, save_draws=False)


# organize all the code, look for bugs, optimize, add comments
# suddenly torunament is a lot slower, check
# make a new model and training
# make a new dataset
