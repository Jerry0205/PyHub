import sys
import os
import pygame
import random
import json
from datetime import datetime

# Absoluter Pfad zur highscores.json im gleichen Verzeichnis wie dieses Skript.
# Falls die Datei noch nicht existiert, wird sie später erstellt.
HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "highscores.json")

# Pygame initialisieren
pygame.init()

# Standardbildschirm-Dimensionen (werden später überschrieben)
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 25
PLAY_WIDTH = 10 * GRID_SIZE
PLAY_HEIGHT = 20 * GRID_SIZE
PLAY_X = (WIDTH - PLAY_WIDTH) // 2
PLAY_Y = HEIGHT - PLAY_HEIGHT - 50

# Definition einiger Farben (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (100, 100, 100)

# Farbkodierungen der Tetrominoes
COLORS = [
    (0, 240, 240),  # Hellblau (I)
    (0, 0, 240),    # Blau (J)
    (240, 160, 0),  # Orange (L)
    (240, 240, 0),  # Gelb (O)
    (0, 240, 0),    # Grün (S)
    (160, 0, 240),  # Lila (T)
    (240, 0, 0)     # Rot (Z)
]

# Definition der Tetromino-Formen (jede Form als Liste von Rotationen)
SHAPES = [
    [
        ['.....',
         '.....',
         '.....',
         'OOOO.',
         '.....'],
        ['.....',
         '..O..',
         '..O..',
         '..O..',
         '..O..']
    ],
    [
        ['.....',
         '.....',
         '..O..',
         '.OOO.',
         '.....'],
        ['.....',
         '..O..',
         '.OO..',
         '..O..',
         '.....'],
        ['.....',
         '.....',
         '.OOO.',
         '..O..',
         '.....'],
        ['.....',
         '..O..',
         '..OO.',
         '..O..',
         '.....']
    ],
    [
        ['.....',
         '.....',
         '..OO.',
         '.OO..',
         '.....'],
        ['.....',
         '.O...',
         '.OO..',
         '..O..',
         '.....']
    ],
    [
        ['.....',
         '.....',
         '.OO..',
         '..OO.',
         '.....'],
        ['.....',
         '..O..',
         '.OO..',
         '.O...',
         '.....']
    ],
    [
        ['.....',
         '.....',
         '.OOO.',
         '.O...',
         '.....'],
        ['.....',
         '.OO..',
         '..O..',
         '..O..',
         '.....'],
        ['.....',
         '.....',
         '...O.',
         '.OOO.',
         '.....'],
        ['.....',
         '.O...',
         '.O...',
         '.OO..',
         '.....']
    ],
    [
        ['.....',
         '.....',
         '.OOO.',
         '...O.',
         '.....'],
        ['.....',
         '..O..',
         '..O..',
         '.OO..',
         '.....'],
        ['.....',
         '.....',
         '.O...',
         '.OOO.',
         '.....'],
        ['.....',
         '.OO..',
         '.O...',
         '.O...',
         '.....']
    ],
    [
        ['.....',
         '.....',
         '.OO..',
         '.OO..',
         '.....']
    ]
]

# Flag zur Speicherung des aktuellen Vollbildmodus-Status
fullscreen_mode = False

def update_display_variables(screen_width, screen_height):
    """
    Aktualisiert die globalen Variablen für Bildschirm und Spielfeld,
    sodass das Spielfeld immer zentriert ist.
    """
    global WIDTH, HEIGHT, PLAY_X, PLAY_Y, GRID_SIZE, PLAY_WIDTH, PLAY_HEIGHT
    WIDTH = screen_width
    HEIGHT = screen_height
    GRID_SIZE = min(WIDTH // 12, HEIGHT // 24)  # Größe der Gitterzelle wird angepasst
    PLAY_WIDTH = 10 * GRID_SIZE
    PLAY_HEIGHT = 20 * GRID_SIZE
    # Zentriere das Spielfeld
    PLAY_X = (WIDTH - PLAY_WIDTH) // 2
    PLAY_Y = (HEIGHT - PLAY_HEIGHT) // 2
    print(f"Display aktualisiert: {WIDTH}x{HEIGHT}, Spielfeld bei ({PLAY_X},{PLAY_Y})")

# --- Klassen und Funktionen für GUI-Elemente und Highscore Verwaltung ---

class Button:
    """
    Eine einfache Button-Klasse, um interaktive Buttons (z. B. im Game Over Screen) zu zeichnen.
    """
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, screen, font):
        # Zeichnet den Button-Hintergrund, wechselt bei Hover den Farbton.
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        # Zeichnet einen Rahmen um den Button.
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        # Aktualisiert den Hover-Status anhand der aktuellen Mausposition.
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        # Gibt True zurück, wenn der Button bei Mausklick getroffen wurde.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hovered
        return False

def load_highscores():
    """
    Lädt Highscores aus der Datei HIGH_SCORE_FILE.
    Falls die Datei noch nicht existiert, wird sie mit einem leeren Array erzeugt.
    """
    try:
        if not os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "w") as file:
                json.dump([], file)
            return []
        with open(HIGH_SCORE_FILE, "r") as file:
            highscores = json.load(file)
            highscores.sort(key=lambda x: x["score"], reverse=True)
            return highscores
    except Exception as e:
        print(f"Fehler beim Laden der Highscores: {e}")
        return []

def save_highscore(name, score):
    """
    Speichert einen neuen Highscore. Falls der Name bereits existiert,
    wird nur überschrieben, wenn der neue Score höher ist.
    """
    try:
        highscores = load_highscores()
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        new_score = {"name": name, "score": score, "date": date}

        existing_entry = None
        for i, entry in enumerate(highscores):
            if entry["name"] == name:
                existing_entry = (i, entry)
                break

        if existing_entry:
            i, entry = existing_entry
            if score > entry["score"]:
                highscores[i] = new_score
                print(f"Highscore für {name} aktualisiert: {entry['score']} -> {score}")
            else:
                print(f"Score {score} nicht gespeichert (niedriger als vorhandener Score {entry['score']})")
                return True
        else:
            highscores.append(new_score)
            print(f"Neuer Highscore für {name}: {score} gespeichert!")

        highscores.sort(key=lambda x: x["score"], reverse=True)
        highscores = highscores[:10]
        with open(HIGH_SCORE_FILE, "w") as file:
            json.dump(highscores, file)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern des Highscores: {e}")
        return False

def get_top_score():
    """
    Gibt den höchsten Highscore zurück oder einen Standardwert, falls keine Highscores vorhanden sind.
    """
    highscores = load_highscores()
    if highscores:
        return highscores[0]
    return {"name": "-----", "score": 0, "date": ""}

# --- Klassen für Texteingabe und Spielobjekte ---

class TextInput:
    """
    Eine einfache Texteingabe-Klasse für die Namenseingabe.
    """
    def __init__(self, x, y, width, font, max_length=10):
        self.rect = pygame.Rect(x, y, width, font.get_height() + 10)
        self.font = font
        self.text = ""
        self.max_length = max_length
        self.active = True
        self.color_active = WHITE
        self.color_inactive = GRAY
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_time = 500  # Blinkzeit in Millisekunden

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        return False

    def update(self):
        # Aktualisiert den Timer zum Blinken des Cursors.
        self.cursor_timer += pygame.time.get_ticks() % 20
        if self.cursor_timer >= self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # Zeichnet das Eingabefeld und den eingegebenen Text.
        pygame.draw.rect(screen, WHITE if self.active else GRAY, self.rect, 2)
        text_surface = self.font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.active and self.cursor_visible:
            cursor_pos = self.font.size(self.text)[0] + self.rect.x + 5
            pygame.draw.line(screen, WHITE,
                             (cursor_pos, self.rect.y + 5),
                             (cursor_pos, self.rect.y + self.rect.height - 5),
                             2)

class Tetromino:
    """
    Repräsentiert ein Tetromino.
    """
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def get_positions(self):
        """
        Gibt eine Liste der (x,y)-Positionen zurück, an denen das Tetromino aktuell gezeichnet wird.
        """
        positions = []
        form = self.shape[self.rotation % len(self.shape)]
        for i, line in enumerate(form):
            for j, column in enumerate(list(line)):
                if column == "O":
                    positions.append((self.x + j, self.y + i))
        return positions

class Tetris:
    """
    Die Hauptklasse des Spiels. Hier wird das Spielfeld verwaltet, neue Tetrominoes erzeugt
    und Spielzustände verwaltet (z. B. Score, Level, Game Over).
    """
    def __init__(self, width, height, player_name):
        self.width = width
        self.height = height
        self.grid = [[BLACK for _ in range(width)] for _ in range(height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 0
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.current_fall_speed = 250  # Start-Fallgeschwindigkeit (ms)
        self.player_name = player_name
        self.held_piece = None
        self.can_hold = True  # Ermöglicht das einmalige Halten eines Stücks pro Drop

        self.highscores = load_highscores()
        self.top_score = get_top_score()
        print(f"Aktueller Top-Score: {self.top_score['score']} von {self.top_score['name']}")

        # Lock-Delay beim Setzen eines Stücks
        self.lock_delay = 400  # 400ms
        self.lock_timer = 0
        self.piece_landed = False

    def try_rotation(self):
        """
        Versucht, das aktuelle Tetromino zu rotieren.
        Falls eine Kollision (z. B. an der Wand) besteht, werden sogenannte Wall-Kicks ausprobiert.
        """
        if self.valid_move(self.current_piece, rotation=1):
            self.current_piece.rotation += 1
            if self.piece_landed:
                self.lock_timer = 0
        else:
            if self.valid_move(self.current_piece, x_offset=-1, rotation=1):
                self.current_piece.x -= 1
                self.current_piece.rotation += 1
                if self.piece_landed:
                    self.lock_timer = 0
            elif self.valid_move(self.current_piece, x_offset=1, rotation=1):
                self.current_piece.x += 1
                self.current_piece.rotation += 1
                if self.piece_landed:
                    self.lock_timer = 0
            elif (self.current_piece.shape == SHAPES[0] and 
                  self.valid_move(self.current_piece, x_offset=-2, rotation=1)):
                self.current_piece.x -= 2
                self.current_piece.rotation += 1
                if self.piece_landed:
                    self.lock_timer = 0
            elif (self.current_piece.shape == SHAPES[0] and 
                  self.valid_move(self.current_piece, x_offset=2, rotation=1)):
                self.current_piece.x += 2
                self.current_piece.rotation += 1
                if self.piece_landed:
                    self.lock_timer = 0

    def hold_piece(self):
        """
        Ermöglicht es dem Spieler, das aktuelle Tetromino zu "halten" (auszuwechseln).
        Wird nur einmal pro Stückzug ausgeführt.
        """
        if not self.can_hold:
            return
        if self.held_piece:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            self.current_piece.x = self.width // 2 - 2
            self.current_piece.y = 0
            self.current_piece.rotation = 0
        else:
            self.held_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        self.can_hold = False
        self.piece_landed = False
        self.lock_timer = 0

    def new_piece(self):
        """
        Erzeugt ein neues Tetromino, das an der Startposition erscheint.
        """
        shape = random.choice(SHAPES)
        return Tetromino(self.width // 2 - 2, 0, shape)
    
    def valid_move(self, piece, x_offset=0, y_offset=0, rotation=0):
        """
        Überprüft, ob eine Bewegung (Verschiebung und/oder Rotation) gültig ist,
        also nicht in einen bereits besetzten Bereich oder außerhalb des Spielfelds führt.
        """
        temp_rotation = (piece.rotation + rotation) % len(piece.shape)
        form = piece.shape[temp_rotation]
        for i, line in enumerate(form):
            for j, column in enumerate(list(line)):
                if column == "O":
                    x = piece.x + j + x_offset
                    y = piece.y + i + y_offset
                    if x < 0 or x >= self.width or y >= self.height:
                        return False
                    if y >= 0 and self.grid[y][x] != BLACK:
                        return False
        return True
    
    def clear_lines(self):
        """
        Löscht volle Zeilen im Gitter, aktualisiert den Punktestand und passt das Level an.
        """
        lines_to_clear = []
        for i in range(self.height):
            if BLACK not in self.grid[i]:
                lines_to_clear.append(i)
        if len(lines_to_clear) == 1:
            self.score += 40 * (self.level + 1)
        elif len(lines_to_clear) == 2:
            self.score += 100 * (self.level + 1)
        elif len(lines_to_clear) == 3:
            self.score += 300 * (self.level + 1)
        elif len(lines_to_clear) == 4:
            self.score += 1200 * (self.level + 1)
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [BLACK for _ in range(self.width)])
        self.lines_cleared += len(lines_to_clear)
        old_level = self.level
        self.level = self.lines_cleared // 10
        if self.level > old_level:
            self.current_fall_speed = max(50, 250 - (self.level * 30))
            print(f"Level up! Neues Level: {self.level}, Geschwindigkeit: {self.current_fall_speed}")
    
    def get_shadow_piece(self):
        """
        Berechnet eine "Schatten"-Version des aktuellen Tetrominos, die anzeigt,
        wo das Stück landen wird.
        """
        if self.game_over:
            return None
        shadow_piece = Tetromino(self.current_piece.x, self.current_piece.y, self.current_piece.shape)
        shadow_piece.rotation = self.current_piece.rotation
        while self.valid_move(shadow_piece, y_offset=1):
            shadow_piece.y += 1
        return shadow_piece
    
    def lock_piece(self):
        """
        Setzt das aktuelle Tetromino endgültig in das Gitter ein (blockiert seine Position),
        löscht nötige Zeilen und prüft, ob das Spiel vorbei ist (Game Over).
        """
        top_blocked = False
        for pos in self.current_piece.get_positions():
            x, y = pos
            if y < 0:
                top_blocked = True
                break
        for pos in self.current_piece.get_positions():
            x, y = pos
            if y >= 0:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        self.piece_landed = False
        self.lock_timer = 0
        if top_blocked or not self.valid_move(self.current_piece):
            self.game_over = True
            is_top_10 = False
            if not self.highscores or self.score > self.highscores[-1]["score"] \
               or len(self.highscores) < 10:
                is_top_10 = True
            if is_top_10:
                print(f"Neuer Highscore für {self.player_name}: {self.score}")
                save_success = save_highscore(self.player_name, self.score)
                if not save_success:
                    print("Fehler: Highscore konnte nicht gespeichert werden!")
                self.highscores = load_highscores()

# --- Zeichenfunktionen für die Spielfeld-Grafik ---

def draw_grid(screen, grid):
    """
    Zeichnet das Spielfeldgitter sowie die darin enthaltenen Blöcke.
    """
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            rect = (PLAY_X + j * GRID_SIZE, PLAY_Y + i * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, grid[i][j], rect, 0)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_piece(screen, piece, is_shadow=False):
    """
    Zeichnet ein Tetromino. Falls der Parameter is_shadow True ist, wird das Stück
    als Schatten (in einer helleren Farbe) gezeichnet.
    """
    if piece is None:
        return
    for pos in piece.get_positions():
        x, y = pos
        if y >= 0:
            color = LIGHT_GRAY if is_shadow else piece.color
            border_color = GRAY if is_shadow else WHITE
            rect = (PLAY_X + x * GRID_SIZE, PLAY_Y + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE)
            if is_shadow:
                pygame.draw.rect(screen, color, rect, 1)
            else:
                pygame.draw.rect(screen, color, rect, 0)
                highlight_rect = (rect[0] + 1, rect[1] + 1,
                                  rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in color),
                                 highlight_rect, 1)
                pygame.draw.rect(screen, border_color, rect, 1)

def draw_next_piece(screen, piece):
    """
    Zeichnet das nächste Tetromino an einer vorgegebenen Position auf dem Bildschirm.
    """
    font = pygame.font.Font(None, 30)
    label = font.render("Next:", True, WHITE)
    screen.blit(label, (WIDTH - 150, 100))
    next_x = WIDTH - 150
    next_y = 150
    form = piece.shape[0]
    for i, line in enumerate(form):
        for j, column in enumerate(list(line)):
            if column == "O":
                rect = (next_x + j * GRID_SIZE, next_y + i * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, piece.color, rect, 0)
                highlight_rect = (rect[0] + 1, rect[1] + 1,
                                  rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in piece.color),
                                 highlight_rect, 1)
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_held_piece(screen, piece):
    """
    Zeichnet das gehaltene Tetromino, falls eines vorhanden ist.
    """
    if piece is None:
        return
    font = pygame.font.Font(None, 30)
    label = font.render("Hold:", True, WHITE)
    screen.blit(label, (30, 200))
    hold_x = 30
    hold_y = 240
    form = piece.shape[0]
    for i, line in enumerate(form):
        for j, column in enumerate(list(line)):
            if column == "O":
                rect = (hold_x + j * GRID_SIZE, hold_y + i * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, piece.color, rect, 0)
                highlight_rect = (rect[0] + 1, rect[1] + 1,
                                  rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in piece.color),
                                 highlight_rect, 1)
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_score(screen, score, level, lines, player_name):
    """
    Zeichnet den Spielername, den aktuellen Score, Level und die Anzahl
    gelöschter Zeilen.
    """
    font = pygame.font.Font(None, 30)
    player_text = font.render(f"Player: {player_name}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lines_text = font.render(f"Lines: {lines}", True, WHITE)
    screen.blit(player_text, (30, 70))
    screen.blit(score_text, (30, 100))
    screen.blit(level_text, (30, 130))
    screen.blit(lines_text, (30, 160))
    help_text = font.render("F: Full Screen  P: Pause  ESC: Titel", True, GRAY)
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 30))

def draw_highscores(screen, highscores, x, y, title="Highscores", show_date=True):
    """
    Zeichnet eine Highscore-Tabelle mit Überschrift, Rang, Namen und Score.
    """
    title_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 24)
    title_text = title_font.render(title, True, YELLOW)
    screen.blit(title_text, (x, y))
    y += 40
    header_rank = text_font.render("Rank", True, WHITE)
    header_name = text_font.render("Name", True, WHITE)
    header_score = text_font.render("Score", True, WHITE)
    screen.blit(header_rank, (x, y))
    screen.blit(header_name, (x + 70, y))
    screen.blit(header_score, (x + 200, y))
    if show_date:
        header_date = text_font.render("Date", True, WHITE)
        screen.blit(header_date, (x + 280, y))
    y += 30
    if not highscores:
        no_scores = text_font.render("No highscores yet!", True, GRAY)
        screen.blit(no_scores, (x + 70, y))
        return
    for i, score in enumerate(highscores[:10]):
        rank_text = text_font.render(f"{i+1}.", True, WHITE)
        name_text = text_font.render(score["name"], True, WHITE)
        score_text = text_font.render(f"{score['score']}", True, WHITE)
        screen.blit(rank_text, (x, y))
        screen.blit(name_text, (x + 70, y))
        screen.blit(score_text, (x + 200, y))
        if show_date and "date" in score:
            date_text = text_font.render(score["date"], True, GRAY)
            screen.blit(date_text, (x + 280, y))
        y += 25

def draw_game_over(screen, score, player_name, highscores):
    """
    Zeichnet den transparenten Game Over-Bildschirm inkl. Score-Informationen
    und interaktiver Buttons.
    """
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    font_button = pygame.font.Font(None, 28)
    game_over_text = font_big.render("GAME OVER", True, RED)
    player_text = font_small.render(f"Player: {player_name}", True, WHITE)
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    shadow_offset = 3
    game_over_shadow = font_big.render("GAME OVER", True, (100, 0, 0))
    screen.blit(game_over_shadow,
                (WIDTH // 2 - game_over_text.get_width() // 2 + shadow_offset,
                 100 + shadow_offset))
    screen.blit(game_over_text,
                (WIDTH // 2 - game_over_text.get_width() // 2, 100))
    screen.blit(player_text,
                (WIDTH // 2 - player_text.get_width() // 2, 180))
    screen.blit(score_text,
                (WIDTH // 2 - score_text.get_width() // 2, 220))
    draw_highscores(screen, highscores, WIDTH // 2 - 200, 270, "Top Scores", False)
    button_width = 220
    button_height = 50
    button_y = HEIGHT - 180
    button_spacing = 20

    # Erstelle Buttons für "Weiterspielen", "Neues Profil" und "Beenden"
    restart_button = Button(
        WIDTH // 2 - button_width - button_spacing,
        button_y,
        button_width,
        button_height,
        "Weiterspielen (R)",
        (0, 100, 0),
        (0, 150, 0),
    )
    new_profile_button = Button(
        WIDTH // 2 + button_spacing,
        button_y,
        button_width,
        button_height,
        "Neues Profil (N)",
        (0, 0, 100),
        (0, 0, 150),
    )
    exit_button = Button(
        WIDTH // 2 - button_width // 2,
        button_y + button_height + button_spacing,
        button_width,
        button_height,
        "Beenden (ESC)",
        (100, 0, 0),
        (150, 0, 0),
    )
    mouse_pos = pygame.mouse.get_pos()
    restart_button.update(mouse_pos)
    new_profile_button.update(mouse_pos)
    exit_button.update(mouse_pos)
    restart_button.draw(screen, font_button)
    new_profile_button.draw(screen, font_button)
    exit_button.draw(screen, font_button)
    return restart_button, new_profile_button, exit_button

def draw_pause_screen(screen):
    """
    Zeichnet einen halbtransparenten Overlay-Bildschirm, der beim Pausieren des Spiels erscheint.
    """
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    pause_text = font_big.render("PAUSED", True, CYAN)
    continue_text = font_small.render("Press P to Continue", True, WHITE)
    shadow_offset = 3
    pause_shadow = font_big.render("PAUSED", True, (0, 50, 80))
    screen.blit(pause_shadow,
                (WIDTH // 2 - pause_text.get_width() // 2 + shadow_offset,
                 HEIGHT // 2 - 50 + shadow_offset))
    screen.blit(pause_text,
                (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(continue_text,
                (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 30))

def toggle_fullscreen(screen):
    """
    Schaltet zwischen Vollbild- und Fenstermodus um.
    """
    global fullscreen_mode
    if not fullscreen_mode:
        print("Wechsel zum Vollbildmodus")
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w, info.current_h
        try:
            screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
            fullscreen_mode = True
            update_display_variables(screen_w, screen_h)
        except Exception as e:
            print(f"Fehler beim Wechsel zum Vollbildmodus: {e}")
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
            fullscreen_mode = True
    else:
        print("Wechsel zum Fenstermodus")
        try:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            fullscreen_mode = False
            update_display_variables(WIDTH, HEIGHT)
        except Exception as e:
            print(f"Fehler beim Wechsel zum Fenstermodus: {e}")
    pygame.event.clear()
    return screen

def name_input_screen(screen):
    """
    Zeigt einen Bildschirm zur Namenseingabe an und gibt den eingegebenen Namen zurück.
    """
    font_big = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    title_text = font_big.render("TETRIS", True, CYAN)
    input_text = font_medium.render("Enter Your Name:", True, WHITE)
    hint_text = font_small.render("(Press ENTER when done)", True, GRAY)
    name_input = TextInput(WIDTH // 2 - 150, HEIGHT // 2, 300, font_medium)
    highscores = load_highscores()
    running = True
    while running:
        screen.fill(BLACK)
        shadow_offset = 3
        title_shadow = font_big.render("TETRIS", True, BLUE)
        screen.blit(title_shadow,
                    (WIDTH // 2 - title_text.get_width() // 2 + shadow_offset,
                     100 + shadow_offset))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(input_text,
                    (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(hint_text,
                    (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 - 20))
        name_input.update()
        name_input.draw(screen)
        draw_highscores(screen, highscores, WIDTH // 2 - 200, HEIGHT // 2 + 50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_f:
                    screen = toggle_fullscreen(screen)
            if name_input.handle_event(event):
                player_name = name_input.text.strip()
                if not player_name:
                    player_name = "Player"
                return player_name

def main(use_existing_player=False, existing_player_name=None):
    """
    Hauptfunktion des Spiels.
    
    WICHTIG: Hier wird der Bildschirm immer im Vollbildmodus gestartet. Dazu werden
    zunächst die aktuellen Bildschirminformationen abgefragt und dann ein
    Vollbildfenster eröffnet. Anschließend werden die Displayvariablen aktualisiert.
    """
    # Start im Vollbildmodus
    info = pygame.display.Info()
    screen = pygame.display.set_mode(
        (info.current_w, info.current_h),
        pygame.FULLSCREEN
    )
    pygame.display.set_caption('Tetris')
    update_display_variables(info.current_w, info.current_h)

    # Namenseingabe – entweder über ein existierendes Profil oder neue Eingabe
    if use_existing_player and existing_player_name:
        player_name = existing_player_name
    else:
        player_name = name_input_screen(screen)

    clock = pygame.time.Clock()

    # Erstelle eine neue Tetris-Instanz (Spielfeld 10x20)
    game = Tetris(10, 20, player_name)
    fall_time = 0
    last_time = pygame.time.get_ticks()

    # Variablen für Button-Handling, Tastaturwiederholungen etc.
    restart_button = None
    new_profile_button = None
    exit_button = None
    key_repeat_time = 0
    key_repeat_delay = 150  # Zeit in ms bis Wiederholung bei gehaltenen Tasten
    key_repeat_interval = 1000 // 7  # Wiederholungsintervall
    move_left = False
    move_right = False
    move_down = False

    running = True
    while running:
        screen.fill(BLACK)
        # Zeichne einen Rahmen um das Spielfeld
        pygame.draw.rect(screen, WHITE,
                         (PLAY_X - 2, PLAY_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4),
                         2)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # ESC schaltet Pausierung um, außer im Game Over-Zustand (dann beendet es das Spiel)
                if event.key == pygame.K_ESCAPE:
                    if game.game_over:
                        running = False
                    else:
                        game.paused = not game.paused
                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        if game.valid_move(game.current_piece, x_offset=-1):
                            game.current_piece.x -= 1
                            if game.piece_landed:
                                game.lock_timer = 0
                        move_left = True
                        key_repeat_time = 0
                    elif event.key == pygame.K_RIGHT:
                        if game.valid_move(game.current_piece, x_offset=1):
                            game.current_piece.x += 1
                            if game.piece_landed:
                                game.lock_timer = 0
                        move_right = True
                        key_repeat_time = 0
                    elif event.key == pygame.K_DOWN:
                        if game.valid_move(game.current_piece, y_offset=1):
                            game.current_piece.y += 1
                        move_down = True
                        key_repeat_time = 0
                    elif event.key == pygame.K_UP:
                        game.try_rotation()
                    elif event.key == pygame.K_SPACE:
                        # "Hard drop" – das Stück wird so weit nach unten bewegt, bis es nicht mehr gültig ist.
                        while game.valid_move(game.current_piece, y_offset=1):
                            game.current_piece.y += 1
                        game.lock_piece()
                    elif event.key == pygame.K_c or event.key == pygame.K_LSHIFT:
                        game.hold_piece()
                    elif event.key == pygame.K_p:
                        game.paused = True
                elif event.key == pygame.K_p and game.paused:
                    game.paused = False
                elif game.game_over:
                    if event.key == pygame.K_r:
                        # Weiterspielen mit gleichem Profil
                        game = Tetris(10, 20, player_name)
                        fall_time = 0
                        last_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_n:
                        # Neues Profil – öffnet den Namenseingabebildschirm erneut
                        player_name = name_input_screen(screen)
                        game = Tetris(10, 20, player_name)
                        fall_time = 0
                        last_time = pygame.time.get_ticks()
                if event.key == pygame.K_f:
                    screen = toggle_fullscreen(screen)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False
                elif event.key == pygame.K_DOWN:
                    move_down = False
            if game.game_over:
                if restart_button and restart_button.is_clicked(event):
                    game = Tetris(10, 20, player_name)
                    fall_time = 0
                    last_time = pygame.time.get_ticks()
                elif new_profile_button and new_profile_button.is_clicked(event):
                    player_name = name_input_screen(screen)
                    game = Tetris(10, 20, player_name)
                    fall_time = 0
                    last_time = pygame.time.get_ticks()
                elif exit_button and exit_button.is_clicked(event):
                    running = False
        if game.paused:
            draw_pause_screen(screen)
            pygame.display.update()
            clock.tick(60)
            continue
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time
        last_time = current_time
        if not game.game_over and not game.paused:
            if move_left or move_right or move_down:
                key_repeat_time += dt
                if key_repeat_time >= key_repeat_delay:
                    if move_left and game.valid_move(game.current_piece, x_offset=-1):
                        game.current_piece.x -= 1
                        if game.piece_landed:
                            game.lock_timer = 0
                    if move_right and game.valid_move(game.current_piece, x_offset=1):
                        game.current_piece.x += 1
                        if game.piece_landed:
                            game.lock_timer = 0
                    if move_down and game.valid_move(game.current_piece, y_offset=1):
                        game.current_piece.y += 1
                    key_repeat_time = key_repeat_delay - key_repeat_interval
            if not game.valid_move(game.current_piece, y_offset=1):
                game.piece_landed = True
                game.lock_timer += dt
                if game.lock_timer >= game.lock_delay:
                    game.lock_piece()
            else:
                game.piece_landed = False
                game.lock_timer = 0
        if not game.game_over:
            fall_time += dt
            if fall_time >= game.current_fall_speed:
                fall_time = 0
                if game.valid_move(game.current_piece, y_offset=1):
                    game.current_piece.y += 1
        draw_grid(screen, game.grid)
        if not game.game_over:
            shadow_piece = game.get_shadow_piece()
            draw_piece(screen, shadow_piece, is_shadow=True)
        if not game.game_over:
            draw_piece(screen, game.current_piece)
        draw_next_piece(screen, game.next_piece)
        draw_held_piece(screen, game.held_piece)
        draw_score(screen, game.score, game.level, game.lines_cleared, game.player_name)
        if game.game_over:
            restart_button, new_profile_button, exit_button = draw_game_over(
                screen, game.score, game.player_name, game.highscores
            )
            restart_button.update(mouse_pos)
            new_profile_button.update(mouse_pos)
            exit_button.update(mouse_pos)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
