import time
from src.game import Game
from src.player import RandomPlayer, HumanPlayer

def play_terminal_game(player1, player2, delay=0.5):
    game = Game()
    # Map players to their symbols
    players = {1: player1, -1: player2}
    
    print("\n" + "="*30)
    print("=== TEEKO TERMINAL DEBUGGER ===")
    print("="*30)
    
    while True:
        # 1. Check for game over
        winner = game.check_game_over()
        if winner is not None:
            print("\nFINAL BOARD:")
            game.board.print_board()
            if winner == 0:
                print("\nRESULT: Game ended in a DRAW (Move limit reached).")
            else:
                print(f"\nRESULT: Player {winner} WINS!")
            break
            
        # 2. Display the board
        print(f"\nMove {game.moves_played}:")
        game.board.print_board()
        
        current_p = players[game.current_player]
        
        # 3. Apply delay ONLY if both players are NOT humans (Bot vs Bot)
        if not isinstance(player1, HumanPlayer) and not isinstance(player2, HumanPlayer):
            time.sleep(delay)
            
        # 4. Get and apply the move
        move = current_p.get_move(game)
        
        if not move:
            print("\nRESULT: No valid moves left. DRAW.")
            break
            
        # 5. Print the action cleanly
        if move[0] == 'drop':
            print(f"--> Player {game.current_player} drops at ({move[1]}, {move[2]})")
        else:
            print(f"--> Player {game.current_player} moves from ({move[1]}, {move[2]}) to ({move[3]}, {move[4]})")
            
        game.make_move(move)

# --- EXECUTION EXAMPLES ---

if __name__ == "__main__":
    # OPTION 1: Bot vs Bot (with 0.5 seconds delay to watch them play)
    p1 = RandomPlayer(1)
    p2 = RandomPlayer(-1)
    play_terminal_game(p1, p2, delay=0.5)
    
    # OPTION 2: Human vs Bot (Uncomment to play against the random bot)
    # p1 = HumanPlayer(1)
    # p2 = RandomPlayer(-1)
    # play_terminal_game(p1, p2)
    
    # OPTION 3: Human vs Human (Uncomment to play against yourself)
    # p1 = HumanPlayer(1)
    # p2 = HumanPlayer(-1)
    # play_terminal_game(p1, p2)