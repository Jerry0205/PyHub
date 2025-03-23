import pygame
import random
from pygame.locals import *
import sys

# Initialisierung von Pygame
pygame.init()

# Fullscreen-Modus: Fenster wird auf volle Bildschirmgröße gesetzt
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Slot Machine mit Kreditsystem")
clock = pygame.time.Clock()
FPS = 60

# Farben
COLORS = {
    "background": (25, 25, 120),
    "button": (34, 139, 34),
    "text": (255, 215, 0),
    "reel_bg": (0, 0, 0),
    "credit": (255, 0, 0)
}

# Spielkonstanten und Parameter
SYMBOLS = ["🍒", "🔔", "💎", "7️⃣", "💵", "🍊"]
WEIGHTS = [10, 8, 5, 3, 7, 12]
PAYOUTS = {
    "🍒🍒🍒": 5,
    "🔔🔔🔔": 10,
    "💎💎💎": 20,
    "7️⃣7️⃣7️⃣": 50,
    "💵💵💵": 100,
    "🍊🍊🍊": 3,
}
INITIAL_BALANCE = 1000
REEL_SIZE = 3

# Dynamische Skalierung der Schriftgrößen
SYMBOL_FONT_SIZE = int(HEIGHT * 0.15)  # z. B. 15% der Bildschirmhöhe
GAME_FONT_SIZE = int(HEIGHT * 0.04)      # z. B. 4% der Bildschirmhöhe

# Kreditparameter
CREDIT_AMOUNT = 500
MAX_CREDITS = 3

class Game:
    def __init__(self):
        self.balance = INITIAL_BALANCE
        self.bet = 50
        self.spinning = False  # Wird auf True gesetzt, sobald ein Spin gestartet wurde
        self.reels = ["🍒", "🍒", "🍒"]
        self.font = pygame.font.SysFont("Arial", GAME_FONT_SIZE)
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
    COOLDOWN = 300  # Minimum Zeitintervall zwischen Klicks in Millisekunden

    def __init__(self, text, x, y, w, h,
                 color=COLORS["button"],
                 font_size=int(HEIGHT * 0.03)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.last_click_time = 0

    def draw(self, surface):
        # Hover-Effekt: Bei Mausüberlagerung wird die Buttonfarbe leicht aufgehellt
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            highlight_color = (
                min(self.color[0] + 40, 255),
                min(self.color[1] + 40, 255),
                min(self.color[2] + 40, 255)
            )
            draw_color = highlight_color
        else:
            draw_color = self.color

        pygame.draw.rect(surface, draw_color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, COLORS["text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < Button.COOLDOWN:
            return False
        self.last_click_time = current_time
        return True

def flush_spin_events(spin_button):
    """
    Entfernt alle MOUSEBUTTONDOWN-Events, die innerhalb des Spin-Button-Bereichs liegen.
    Dadurch werden z.B. nach schnellen Klicks zusätzliche Spin-Events aus der Queue
    entfernt.
    """
    events = pygame.event.get(pygame.MOUSEBUTTONDOWN)
    for event in events:
        if not spin_button.rect.collidepoint(event.pos):
            pygame.event.post(event)
    # Hinweis: Events, die den Spin-Button betreffen, werden verworfen.

def draw_game(screen, game, buttons):
    screen.fill(COLORS["background"])

    # Anzeige von Guthaben und Gewinn
    balance_text = game.font.render(
        f"Guthaben: ${game.balance:.2f}", True, COLORS["text"]
    )
    screen.blit(balance_text, (20, 20))
    if game.last_win > 0:
        win_text = game.font.render(
            f"Gewinn: ${game.last_win:.2f}", True, COLORS["text"]
        )
        screen.blit(win_text, (20, 20 + GAME_FONT_SIZE + 10))
    
    # Anzeige von Kreditstatus und Schulden
    credit_text = game.font.render(
        f"Kredite: {game.credits_taken}/{MAX_CREDITS}", True, COLORS["text"]
    )
    screen.blit(credit_text, (20, 20 + 2 * (GAME_FONT_SIZE + 10)))
    if game.credit_debt > 0:
        debt_text = game.font.render(
            f"Schulden: ${game.credit_debt:.2f}", True, COLORS["credit"]
        )
        screen.blit(debt_text, (20, 20 + 3 * (GAME_FONT_SIZE + 10)))

    # Walzen (centrisch zeichnen)
    total_width = REEL_SIZE * SYMBOL_FONT_SIZE + (REEL_SIZE - 1) * 40
    reel_x = (WIDTH - total_width) // 2
    for i, symbol in enumerate(game.reels):
        text_surf = game.symbol_font.render(symbol, True, COLORS["text"])
        text_rect = text_surf.get_rect(
            center=(
                reel_x + i * (SYMBOL_FONT_SIZE + 40) + SYMBOL_FONT_SIZE // 2,
                HEIGHT // 2,
            )
        )
        pygame.draw.rect(
            screen,
            COLORS["reel_bg"],
            text_rect.inflate(20, 20),
            border_radius=10
        )
        screen.blit(text_surf, text_rect)

    # Zeichnen aller Buttons
    for btn in buttons:
        btn.draw(screen)

    pygame.display.flip()

def handle_spin(game, buttons, spin_button):
    if game.balance < game.bet:
        # Falls nicht genügend Guthaben vorhanden ist
        game.spinning = False
        spin_button.text = "SPIN"
        return

    game.balance -= game.bet

    # Spin-Animation: 10 schnelle Animationen (insgesamt ca. 800ms)
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
    spin_button.text = "SPIN"

def handle_all_in(game):
    game.bet = game.balance
    return f"BET: ${game.bet}"

def main():
    game = Game()

    # Dynamische Button-Größen (relativ zur Bildschirmgröße)
    BUTTON_WIDTH = int(WIDTH * 0.2)
    BUTTON_HEIGHT = int(HEIGHT * 0.1)
    margin_bottom = int(HEIGHT * 0.05)
    gap = int(HEIGHT * 0.02)
    bottom_y = HEIGHT - BUTTON_HEIGHT - margin_bottom
    credit_y = bottom_y - BUTTON_HEIGHT - gap

    # Untere Zeile: SPIN, BET, ALL-IN
    spin_button = Button(
        "SPIN",
        WIDTH // 4 - BUTTON_WIDTH // 2,
        bottom_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    bet_button = Button(
        f"BET: ${game.bet}",
        WIDTH // 2 - BUTTON_WIDTH // 2,
        bottom_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    all_in_button = Button(
        "ALL-IN",
        WIDTH * 3 // 4 - BUTTON_WIDTH // 2,
        bottom_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    # Nächste Zeile: KREDIT, ZURÜCKZAHLEN
    credit_button = Button(
        "KREDIT",
        WIDTH // 4 - BUTTON_WIDTH // 2,
        credit_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        color=COLORS["credit"],
    )
    repay_button = Button(
        "ZURÜCKZAHLEN",
        WIDTH * 3 // 4 - BUTTON_WIDTH // 2,
        credit_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        color=COLORS["credit"],
    )

    # BEENDEN-Button (in der oberen rechten Ecke, gleiche Größe wie die anderen)
    exit_button = Button(
        "BEENDEN",
        WIDTH - BUTTON_WIDTH - int(WIDTH * 0.02),
        int(HEIGHT * 0.02),
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        color=(200, 0, 0),
    )

    buttons = [spin_button, bet_button, all_in_button,
               credit_button, repay_button, exit_button]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Der BEENDEN-Button soll immer reagieren
                if exit_button.is_clicked(mouse_pos):
                    running = False

                # Wenn der Spin-Button gedrückt wird und kein Spin läuft,
                # wird er sofort gesperrt
                elif spin_button.is_clicked(mouse_pos) and not game.spinning:
                    game.spinning = True
                    spin_button.text = "SPINNING..."
                    handle_spin(game, buttons, spin_button)
                    flush_spin_events(spin_button)

                # Andere Buttons nur verarbeiten, wenn kein Spin läuft
                elif not game.spinning:
                    if bet_button.is_clicked(mouse_pos):
                        if game.bet == 50:
                            game.bet = 25
                        elif game.bet == 25:
                            game.bet = 100
                        else:
                            game.bet = 50
                        bet_button.text = f"BET: ${game.bet}"
                    elif all_in_button.is_clicked(mouse_pos):
                        bet_button.text = handle_all_in(game)
                    elif credit_button.is_clicked(mouse_pos):
                        game.take_credit()
                    elif repay_button.is_clicked(mouse_pos):
                        game.repay_credit()

        draw_game(screen, game, buttons)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
