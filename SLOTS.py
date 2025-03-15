import pygame
import random
from pygame.locals import *
import sys

# Initialisierung
pygame.init()

# Fenstereinstellungen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slot Machine mit Kreditsystem")
clock = pygame.time.Clock()
FPS = 60

# Farben
COLORS = {
    "background": (25, 25, 112),
    "button": (34, 139, 34),
    "text": (255, 215, 0),
    "reel_bg": (0, 0, 0),
    "credit": (255, 0, 0)
}

# Spielkonstanten
SYMBOLS = ["🍒", "🔔", "💎", "7️⃣", "💵", "🍊"]
WEIGHTS = [10, 8, 5, 3, 7, 12]
PAYOUTS = {
    "🍒🍒🍒": 5, "🔔🔔🔔": 10, "💎💎💎": 20,
    "7️⃣7️⃣7️⃣": 50, "💵💵💵": 100, "🍊🍊🍊": 3
}
INITIAL_BALANCE = 1000
REEL_SIZE = 3
SYMBOL_FONT_SIZE = 74
CREDIT_AMOUNT = 500
MAX_CREDITS = 3

class Game:
    def __init__(self):
        self.balance = INITIAL_BALANCE
        self.bet = 50
        self.spinning = False
        self.reels = ["🍒", "🍒", "🍒"]
        self.font = pygame.font.SysFont("Arial", 36)
        self.symbol_font = pygame.font.SysFont("Segoe UI Emoji", SYMBOL_FONT_SIZE)
        self.last_win = 0
        self.credits_taken = 0
        self.credit_debt = 0

    def spin_reels(self):
        return random.choices(SYMBOLS, weights=WEIGHTS, k=REEL_SIZE)

    def calculate_payout(self):
        combo = "".join(self.reels)
        if combo in PAYOUTS:
            return self.bet * PAYOUTS[combo]
        if len(set(self.reels)) == 2:
            return self.bet * 2
        return 0

    def take_credit(self):
        if self.credits_taken < MAX_CREDITS:
            self.balance += CREDIT_AMOUNT
            self.credits_taken += 1
            interest_rate = 0.05 * self.credits_taken
            self.credit_debt += CREDIT_AMOUNT * (1 + interest_rate)

    def repay_credit(self):
        if self.credit_debt > 0 and self.balance >= self.credit_debt:
            self.balance -= self.credit_debt
            self.credit_debt = 0
            self.credits_taken = 0
            return True
        return False

class Button:
    def __init__(self, text, x, y, w=200, h=50, color=COLORS["button"]):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, COLORS["text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def draw_game(screen, game, buttons):
    screen.fill(COLORS["background"])
    
    # Balance und Gewinn Anzeige
    balance_text = game.font.render(f"Guthaben: ${game.balance:.2f}", True, COLORS["text"])
    screen.blit(balance_text, (20, 20))
    if game.last_win > 0:
        win_text = game.font.render(f"Gewinn: ${game.last_win:.2f}", True, COLORS["text"])
        screen.blit(win_text, (20, 60))
    
    # Kreditstatus anzeigen
    credit_text = game.font.render(f"Kredite: {game.credits_taken}/{MAX_CREDITS}", True, COLORS["text"])
    screen.blit(credit_text, (20, 100))
    if game.credit_debt > 0:
        debt_text = game.font.render(f"Schulden: ${game.credit_debt:.2f}", True, COLORS["credit"])
        screen.blit(debt_text, (20, 140))
    
    # Walzen zeichnen
    reel_x = WIDTH // 2 - (SYMBOL_FONT_SIZE * REEL_SIZE // 2)
    for i, symbol in enumerate(game.reels):
        text_surf = game.symbol_font.render(symbol, True, COLORS["text"])
        text_rect = text_surf.get_rect(center=(reel_x + i * (SYMBOL_FONT_SIZE + 40), HEIGHT // 2))
        pygame.draw.rect(screen, COLORS["reel_bg"], text_rect.inflate(20,20), border_radius=10)
        screen.blit(text_surf, text_rect)
    
    # Buttons zeichnen
    for btn in buttons:
        btn.draw(screen)
    
    pygame.display.flip()

def handle_spin(game, buttons):
    if game.balance < game.bet:
        return False
    
    game.balance -= game.bet
    game.spinning = True
    
    for _ in range(10):
        game.reels = game.spin_reels()
        draw_game(screen, game, buttons)
        pygame.display.update()
        pygame.time.wait(80)
    
    payout = game.calculate_payout()
    game.last_win = payout
    if payout > 0:
        game.balance += payout
    
    game.spinning = False

def handle_all_in(game):
    game.bet = game.balance
    return f"BET: ${game.bet}"

def main():
    game = Game()
    
    buttons = [
        Button("SPIN", WIDTH // 4 - 100, HEIGHT - 100),
        Button(f"BET: ${game.bet}", WIDTH // 2 - 100, HEIGHT - 100),
        Button("ALL-IN", WIDTH * 3 // 4 - 100, HEIGHT - 100),
        Button("KREDIT", WIDTH // 4 - 100, HEIGHT - 180, color=COLORS["credit"]),
        Button("ZURÜCKZAHLEN", WIDTH * 3 // 4 - 100, HEIGHT - 180, color=COLORS["credit"]),
        Button("BEENDEN", WIDTH - 120, 20, w=100, h=40, color=(200, 0, 0))  # Neuer BEENDEN Button
    ]
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if event.type == MOUSEBUTTONDOWN:
                if buttons[0].is_clicked(mouse_pos) and not game.spinning:
                    handle_spin(game, buttons)
                elif buttons[1].is_clicked(mouse_pos):
                    game.bet = 25 if game.bet == 100 else 50 if game.bet == 25 else 100
                    buttons[1].text = f"BET: ${game.bet}"
                elif buttons[2].is_clicked(mouse_pos):
                    buttons[1].text = handle_all_in(game)
                elif buttons[3].is_clicked(mouse_pos):
                    game.take_credit()
                elif buttons[4].is_clicked(mouse_pos):
                    game.repay_credit()
                elif buttons[5].is_clicked(mouse_pos):  # Neuer BEENDEN Button Handler
                    running = False
        
        draw_game(screen, game, buttons)
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
