import time
import os
from src.game import Game
from src.player import RandomPlayer, TerminalPlayer, SmartPlayer, MinimaxPlayer

def clear_screen():
    """Clears the terminal screen for a clean UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def play_terminal_game(player1, player2, delay=0.5):
    game = Game()
    players = {1: player1, -1: player2}
    
    # Check if there's a human playing to adjust UI flow
    has_human = isinstance(player1, TerminalPlayer) or isinstance(player2, TerminalPlayer)
    moves_count = 1
    
    clear_screen()
    
    while True:
        # 1. UI Header
        print("\n" + "="*35)
        print("      === TEEKO ARENA ===")
        print("="*35)
        
        # 2. Check for game over
        winner = game.check_game_over()
        if winner != 0:
            print("\nFINAL BOARD:")
            game.board.print_board()
            print(f"\n🏆 RESULT: Player {winner} WINS! 🏆\n")
            break
            
        # 3. Display the board
        print(f"\nTurn: {moves_count} | Phase: {game.phase.upper()}")
        game.board.print_board()
        
        current_p = players[game.current_player]
        
        # 4. Apply delay ONLY if it's Bot vs Bot
        if not has_human:
            time.sleep(delay)
            clear_screen() # Clear before next bot move
            
        # 5. Get move
        move = current_p.get_move(game)
        
        if not move:
            print("\nRESULT: No valid moves left. DRAW.")
            break
            
        # 6. Apply move
        game.make_move(move)
        moves_count += 1
        
        # 7. Clean up for human players
        if has_human:
            clear_screen()
            # Print last action so human knows what the bot did
            if move[0] == 'drop':
                print(f"[!] Player {game.current_player * -1} dropped at ({move[1]}, {move[2]})")
            else:
                print(f"[!] Player {game.current_player * -1} moved from ({move[1]}, {move[2]}) to ({move[3]}, {move[4]})")


# --- EXECUTION MENU ---
if __name__ == "__main__":
    clear_screen()
    print("Welcome to Teeko Debugger")
    print("1. Watch: Bot vs Bot")
    print("2. Play: Human vs Bot")
    print("3. Play: Human vs Human")
    
    choice = input("\nSelect mode (1/2/3): ").strip()
    if choice == '1':
            p1 = SmartPlayer(model_path=os.path.join('data', 'model1.keras'), player_id=1)
            p2 = MinimaxPlayer(model_path=os.path.join('data', 'model1.keras'), player_id=-1, depth=2)
            play_terminal_game(p1, p2, delay=0)
    elif choice == '2':
        # You play as Player 1, Bot is Player -1
        play_terminal_game(TerminalPlayer(), RandomPlayer())
    elif choice == '3':
        play_terminal_game(TerminalPlayer(), TerminalPlayer())
    else:
        print("Invalid choice. Exiting.")


