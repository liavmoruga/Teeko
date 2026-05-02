import pygame
import sys
import os

try:
    from src.game import Game
    from src.player import RandomPlayer
except ImportError:
    print("Error: Run this script from the root project directory.")
    sys.exit()

# --- CONSTANTS ---
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 700
BOARD_MARGIN = 50
SQUARE_SIZE = (WINDOW_WIDTH - 2 * BOARD_MARGIN) // 5
PIECE_RADIUS = SQUARE_SIZE // 2 - 10

# Colors
WHITE, BG_COLOR = (255, 255, 255), (245, 245, 250)
TEXT_COLOR, GRID_COLOR = (40, 40, 40), (100, 100, 100)
HIGHLIGHT_COLOR = (255, 255, 180)

# Piece & Hint Colors: {Player_ID: (Fill, Border, Hint_Color)}
PIECE_COLORS = {
    1: ((80, 80, 80), (30, 30, 30), (180, 180, 180)),   # Black
   -1: ((220, 50, 50), (150, 20, 20), (255, 150, 150))  # Red
}

class Button:
    """Enhanced UI Button with smooth hover animation."""
    def __init__(self, x, y, w, h, text, font, bg_color=(220, 220, 220)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.font, self.bg_color = text, font, bg_color
        self.hover_offset = 0 

    def draw(self, surface, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        self.hover_offset = 2 if is_hovered else 0
        
        # Calculate color slightly brighter on hover
        color = (min(self.bg_color[0]+20, 255), min(self.bg_color[1]+20, 255), min(self.bg_color[2]+20, 255)) if is_hovered else self.bg_color
        
        # Draw shadow
        pygame.draw.rect(surface, (150, 150, 150), self.rect.move(2, 4), border_radius=10)
        
        # Draw main button (moves slightly up on hover)
        draw_rect = self.rect.move(0, -self.hover_offset)
        pygame.draw.rect(surface, color, draw_rect, border_radius=10)
        pygame.draw.rect(surface, GRID_COLOR, draw_rect, 2, border_radius=10)
        
        # Draw text (smooth rendering)
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(text_surf, text_surf.get_rect(center=draw_rect.center))

class TeekoGUI:
    def __init__(self, available_bots=None):
        pygame.init()
        pygame.display.set_caption("Teeko")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 20)
        self.clock = pygame.time.Clock()
        
        self.options = ["Human"] + list((available_bots or {}).keys())
        self.bots = available_bots or {}
        self.p1_idx = self.p2_idx = 0
        
        self.state = "MENU"
        self.btn_p1 = Button(100, 250, 400, 50, "", self.font)
        self.btn_p2 = Button(100, 330, 400, 50, "", self.font)
        self.btn_start = Button(200, 450, 200, 60, "START GAME", self.font, (150, 220, 150))
        
        self.game = None
        self.selected_square = None
        self.is_dragging = False
        self.just_selected = False 
        self.valid_destinations = []

    def start_game(self):
        self.game, self.state = Game(), "PLAYING"
        self.selected_square, self.is_dragging = None, False
        self.just_selected, self.valid_destinations = False, []
        p1, p2 = self.options[self.p1_idx], self.options[self.p2_idx]
        self.players = {
            1: "Human" if p1 == "Human" else self.bots[p1],
           -1: "Human" if p2 == "Human" else self.bots[p2]
        }

    def get_square(self, pos):
        row, col = (pos[1] - 150) // SQUARE_SIZE, (pos[0] - BOARD_MARGIN) // SQUARE_SIZE
        return (int(row), int(col)) if 0 <= row < 5 and 0 <= col < 5 else None

    def get_center(self, row, col):
        return (BOARD_MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, 150 + row * SQUARE_SIZE + SQUARE_SIZE // 2)

    def draw_piece(self, player_val, pos):
        fill_color, border_color, _ = PIECE_COLORS[player_val]
        pygame.draw.circle(self.screen, fill_color, pos, PIECE_RADIUS)
        pygame.draw.circle(self.screen, border_color, pos, PIECE_RADIUS, 3)

    def draw_board(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        
        # UI Text
        self.screen.blit(self.font.render(f"Phase: {self.game.phase.upper()}", True, TEXT_COLOR), (BOARD_MARGIN, 30))
        turn_str = "Black" if self.game.current_player == 1 else "Red"
        self.screen.blit(self.small_font.render(f"Turn: {turn_str}", True, GRID_COLOR), (BOARD_MARGIN, 70))
        
        # Grid
        board_rect = pygame.Rect(BOARD_MARGIN, 150, SQUARE_SIZE*5, SQUARE_SIZE*5)
        pygame.draw.rect(self.screen, WHITE, board_rect, border_radius=5)
        pygame.draw.rect(self.screen, GRID_COLOR, board_rect, 3, border_radius=5)
        
        for r in range(5):
            for c in range(5):
                rect = pygame.Rect(BOARD_MARGIN + c * SQUARE_SIZE, 150 + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                if self.selected_square == (r, c):
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, rect)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        # Hints logic - ONLY IF IT'S A HUMAN'S TURN
        if self.players[self.game.current_player] == "Human":
            hint_color = PIECE_COLORS[self.game.current_player][2]
            if self.game.phase == 'drop':
                for r in range(5):
                    for c in range(5):
                        if self.game.board.grid[r][c] == 0:
                            pygame.draw.circle(self.screen, hint_color, self.get_center(r, c), 15)
            else:
                for r, c in self.valid_destinations:
                    pygame.draw.circle(self.screen, hint_color, self.get_center(r, c), 15)

        # Pieces
        for r in range(5):
            for c in range(5):
                val = self.game.board.grid[r][c]
                if val != 0 and not (self.is_dragging and self.selected_square == (r, c)):
                    self.draw_piece(val, self.get_center(r, c))

        # Dragged Piece
        if self.is_dragging and self.selected_square:
            val = self.game.board.grid[self.selected_square[0]][self.selected_square[1]]
            self.draw_piece(val, mouse_pos)

    def draw_menu(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        title = pygame.font.SysFont("Segoe UI", 48, bold=True).render("TEEKO", True, TEXT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        subtitle = pygame.font.SysFont("Segoe UI", 24, italic=True).render("Liav Moruga", True, GRID_COLOR)
        self.screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 135))
        
        self.btn_p1.text = f"Black: {self.options[self.p1_idx]}"
        self.btn_p2.text = f"Red: {self.options[self.p2_idx]}"
        for btn in (self.btn_p1, self.btn_p2, self.btn_start):
            btn.draw(self.screen, mouse_pos)

    def draw_game_over(self, mouse_pos):
        self.draw_board(mouse_pos)
        winner = self.game.check_game_over()
        msg, color = ("BLACK WINS!", PIECE_COLORS[1][0]) if winner == 1 else ("RED WINS!", PIECE_COLORS[-1][0]) if winner == -1 else ("DRAW!", TEXT_COLOR)
            
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((245, 245, 250, 220))
        self.screen.blit(overlay, (0, 0))
        
        text_surf = pygame.font.SysFont("Segoe UI", 50, bold=True).render(msg, True, color)
        self.screen.blit(text_surf, (WINDOW_WIDTH//2 - text_surf.get_width()//2, WINDOW_HEIGHT//2 - 60))

    def handle_click(self, event):
        if event.button != 1: return
        sq = self.get_square(event.pos)
        if not sq: return
        
        r, c = sq
        moves = self.game.get_valid_moves()
        
        if self.game.phase == 'drop':
            if ('drop', r, c) in moves:
                self.game.make_move(('drop', r, c))
                
        elif self.game.phase == 'move':
            if sq in self.valid_destinations and self.selected_square:
                # Clicked a valid hint to move
                self.game.make_move(('move', *self.selected_square, r, c))
                self.selected_square, self.valid_destinations = None, []
            elif self.game.board.grid[r][c] == self.game.current_player:
                if self.selected_square == sq:
                    # Already selected! Start dragging, but mark that we didn't JUST select it
                    self.is_dragging = True
                    self.just_selected = False
                else:
                    # Select new piece
                    self.selected_square, self.is_dragging = sq, True
                    self.valid_destinations = [(m[3], m[4]) for m in moves if m[0] == 'move' and m[1] == r and m[2] == c]
                    self.just_selected = True
            else:
                self.selected_square, self.valid_destinations = None, []

    def run(self):
        mouse_pos = (0,0)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    
                if self.state == "MENU" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_p1.rect.collidepoint(event.pos): self.p1_idx = (self.p1_idx + 1) % len(self.options)
                    elif self.btn_p2.rect.collidepoint(event.pos): self.p2_idx = (self.p2_idx + 1) % len(self.options)
                    elif self.btn_start.rect.collidepoint(event.pos): self.start_game()
                            
                elif self.state == "PLAYING":
                    if self.players[self.game.current_player] == "Human":
                        if event.type == pygame.MOUSEBUTTONDOWN: 
                            self.handle_click(event)
                            
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_dragging:
                            self.is_dragging = False
                            sq = self.get_square(event.pos)
                            
                            if sq and sq in self.valid_destinations:
                                # Successful Drag and Drop
                                self.game.make_move(('move', *self.selected_square, *sq))
                                self.selected_square, self.valid_destinations = None, []
                            elif sq == self.selected_square and not self.just_selected:
                                # DESELECT: Released on the same square AND it was already selected before
                                self.selected_square, self.valid_destinations = None, []
                                
                elif self.state == "GAME_OVER" and event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = "MENU"

            if self.state == "PLAYING":
                if self.game.check_game_over() != 0: self.state = "GAME_OVER"
                elif self.players[self.game.current_player] != "Human":
                    # Force screen update so the last move is visible before bot calculates
                    self.draw_board(mouse_pos)
                    pygame.display.flip()
                    
                    start_time = pygame.time.get_ticks()
                    move = self.players[self.game.current_player].get_move(self.game)
                    calc_time = pygame.time.get_ticks() - start_time
                    
                    # Pad the time only if the bot was faster than 500ms
                    if calc_time < 500:
                        pygame.time.delay(500 - calc_time)
                        
                    if move: self.game.make_move(move)
                    else: self.state = "GAME_OVER"

            if self.state == "MENU": self.draw_menu(mouse_pos)
            elif self.state == "PLAYING" and self.players[self.game.current_player] == "Human": self.draw_board(mouse_pos)
            elif self.state == "GAME_OVER": self.draw_game_over(mouse_pos)
                
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    # Add your bots here!
    bots = {"Random Bot": RandomPlayer()}
    TeekoGUI(available_bots=bots).run()