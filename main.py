from src.player import RandomPlayer, SmartPlayer, MinimaxPlayer
from src.tournament import Tournament
import time
import os


def f1():
    print("Goal: High signal, precise endgame data to prove model capability.")
    p1 = RandomPlayer()
    p2 = RandomPlayer()
    t = Tournament(p1, p2, num_games=20000)
    t.play(
            save_dataset=True, 
            filename="dataset.csv",
            max_moves=80,             
            moves_before_finish=12,   # Only the very end of the game
            gamma=0.90,               
            min_diff=0.08,            # Strict filtering
            save_draws=False          
        )
    

def f2():
    print("Goal: Deep context, mid-game strategy, massive dataset.")
    p1 = RandomPlayer()
    p2 = RandomPlayer()
    t = Tournament(p1, p2, num_games=100000)
    t.play(
            save_dataset=True, 
            max_moves=100,             
            moves_before_finish=25,   # Look deep into the mid-game
            gamma=0.85,               # Steeper decay because we look further back
            min_diff=0.05,            # Looser filtering to catch subtle advantages
            save_draws=False          
        )

def f3():
    p1 = SmartPlayer(model_path=os.path.join('data', 'model1.keras'), player_id=1)
    p2 = MinimaxPlayer(model_path=os.path.join('data', 'model1.keras'), player_id=-1, depth=3)
    t = Tournament(p1, p2, num_games=10)
    t.play(save_dataset=False)



if __name__ == "__main__":
    
    start_time = time.time()
    f3()
    end_time = time.time()
    print(f"Total time elapsed: {end_time - start_time:.2f} seconds.")

