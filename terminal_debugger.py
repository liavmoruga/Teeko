import os
import time
from src.game import Game
from src.player import RandomPlayer
# from src.player import SmartPlayer, MinimaxPlayer

def clear():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_human_move(game):
    """Handles terminal input for a human player."""
    valid_moves = game.get_valid_moves()
    if not valid_moves: 
        return None
        
    while True:
        try:
            prompt = "DROP (r c) >> " if game.phase == 'drop' else "MOVE (r1 c1 r2 c2) >> "
            inp = [int(x) for x in input(prompt).strip().split()]
            move = ('drop', inp[0], inp[1]) if game.phase == 'drop' else ('move', inp[0], inp[1], inp[2], inp[3])
            
            if move in valid_moves: 
                return move
            print("Illegal move.")
        except (ValueError, IndexError):
            print("Invalid format. Use numbers separated by spaces.")

def run_terminal_arena(bots):
    clear()
    print("=== TEEKO TERMINAL ===")
    options = ["Human"] + list(bots.keys())
    for i, opt in enumerate(options): 
        print(f"{i}. {opt}")
    
    try:
        players = {
            1: "Human" if (p1 := options[int(input("\nSelect P1 (Black): "))]) == "Human" else bots[p1],
           -1: "Human" if (p2 := options[int(input("Select P2 (Red): "))]) == "Human" else bots[p2]
        }
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return
        
    game = Game()
    clear()
    
    while game.check_game_over() == 0:
        print(f"Phase: {game.phase.upper()} | Turn: {'Black (1)' if game.current_player == 1 else 'Red (-1)'}")
        game.board.print_board()
        
        current_p = players[game.current_player]
        
        if current_p != "Human":
            time.sleep(0.5)
            
        move = get_human_move(game) if current_p == "Human" else current_p.get_move(game)
        
        if not move: 
            break
            
        game.make_move(move)
        clear()
        
        action = f"dropped at {move[1]},{move[2]}" if move[0] == 'drop' else f"moved {move[1]},{move[2]} -> {move[3]},{move[4]}"
        print(f"Player {game.current_player * -1} {action}\n")
        
    game.board.print_board()
    winner = game.check_game_over()
    print(f"RESULT: {'DRAW' if winner == 0 else f'Player {winner} WINS'}")

if __name__ == "__main__":
    # Add available bots here
    available_bots = {
        "Random Bot": RandomPlayer()
    }
    run_terminal_arena(available_bots)