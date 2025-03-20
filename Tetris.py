import sys
import os
import pygame
import random
import json
from datetime import datetime

# Pygame initialisieren
pygame.init()

# Bildschirm-Dimensionen
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 25
PLAY_WIDTH = 10 * GRID_SIZE
PLAY_HEIGHT = 20 * GRID_SIZE
PLAY_X = (WIDTH - PLAY_WIDTH) // 2
PLAY_Y = HEIGHT - PLAY_HEIGHT - 50

# Farben
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

# Tetromino-Farben - verschönerte Varianten
COLORS = [
    (0, 240, 240),  # Hellblau (I)
    (0, 0, 240),    # Blau (J)
    (240, 160, 0),  # Orange (L)
    (240, 240, 0),  # Gelb (O)
    (0, 240, 0),    # Grün (S)
    (160, 0, 240),  # Lila (T)
    (240, 0, 0)     # Rot (Z)
]

# Tetromino-Formen
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

# Globale Flag für Vollbildmodus
fullscreen_mode = False

# Funktion zum Aktualisieren der Bildschirmvariablen
def update_display_variables(screen_width, screen_height):
    global WIDTH, HEIGHT, PLAY_X, PLAY_Y, GRID_SIZE, PLAY_WIDTH, PLAY_HEIGHT
    
    WIDTH = screen_width
    HEIGHT = screen_height
    
    # Spielfeldgröße an Bildschirm anpassen
    GRID_SIZE = min(WIDTH // 12, HEIGHT // 24)
    PLAY_WIDTH = 10 * GRID_SIZE
    PLAY_HEIGHT = 20 * GRID_SIZE
    
    # Spielfeld-Position zentrieren
    PLAY_X = (WIDTH - PLAY_WIDTH) // 2
    PLAY_Y = (HEIGHT - PLAY_HEIGHT) // 2
    
    print(f"Display aktualisiert: {WIDTH}x{HEIGHT}, Spielfeld bei ({PLAY_X},{PLAY_Y})")

# Button-Klasse für bessere Benutzeroberfläche
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self, screen, font):
        # Button Hintergrund
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        # Button Rahmen
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Button Text
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hovered
        return False

# Highscore-Funktionen mit Spielernamen
def load_highscores():
    try:
        if os.path.exists("highscores.json"):
            with open("highscores.json", "r") as file:
                highscores = json.load(file)
                # Sortieren nach Punktestand (absteigend)
                highscores.sort(key=lambda x: x["score"], reverse=True)
                return highscores
        return []
    except Exception as e:
        print(f"Fehler beim Laden der Highscores: {e}")
        return []

def save_highscore(name, score):
    try:
        highscores = load_highscores()
        
        # Datum und Uhrzeit hinzufügen
        date = datetime.now().strftime("%d.%m.%Y %H:%M")
        new_score = {"name": name, "score": score, "date": date}
        
        # Überprüfen, ob der Name bereits existiert
        existing_entry = None
        for i, entry in enumerate(highscores):
            if entry["name"] == name:
                existing_entry = (i, entry)
                break
                
        if existing_entry:
            i, entry = existing_entry
            # Nur überschreiben, wenn der neue Score höher ist
            if score > entry["score"]:
                highscores[i] = new_score
                print(f"Highscore für {name} aktualisiert: {entry['score']} -> {score}")
            else:
                print(f"Score {score} nicht gespeichert (niedriger als bestehender Score {entry['score']})")
                return True  # Erfolgreich, auch wenn nicht gespeichert (kein Fehler)
        else:
            # Neuen Score hinzufügen, wenn Name noch nicht vorhanden
            highscores.append(new_score)
            print(f"Neuer Highscore für {name}: {score} gespeichert!")
        
        # Nach Punkten sortieren
        highscores.sort(key=lambda x: x["score"], reverse=True)
        
        # Auf die Top 10 begrenzen
        highscores = highscores[:10]
        
        # Speichern
        with open("highscores.json", "w") as file:
            json.dump(highscores, file)
            
        return True
    except Exception as e:
        print(f"Fehler beim Speichern des Highscores: {e}")
        return False

def get_top_score():
    highscores = load_highscores()
    if highscores:
        return highscores[0]
    return {"name": "-----", "score": 0, "date": ""}

# Texteingabe-Klasse
class TextInput:
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
        self.cursor_blink_time = 500  # Millisekunden

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
        # Cursor-Blinken
        self.cursor_timer += pygame.time.get_ticks() % 20
        if self.cursor_timer >= self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # Eingabefeld zeichnen
        pygame.draw.rect(screen, WHITE if self.active else GRAY, self.rect, 2)
        
        # Text zeichnen
        text_surface = self.font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # Cursor zeichnen
        if self.active and self.cursor_visible:
            cursor_pos = self.font.size(self.text)[0] + self.rect.x + 5
            pygame.draw.line(screen, WHITE, 
                            (cursor_pos, self.rect.y + 5), 
                            (cursor_pos, self.rect.y + self.rect.height - 5), 
                            2)

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def get_positions(self):
        positions = []
        form = self.shape[self.rotation % len(self.shape)]
        
        for i, line in enumerate(form):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'O':
                    positions.append((self.x + j, self.y + i))
                    
        return positions

class Tetris:
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
        self.current_fall_speed = 250  # Erhöhte Fallgeschwindigkeit
        self.player_name = player_name
        self.held_piece = None
        self.can_hold = True  # Kann nur einmal pro Tetromino verwendet werden
        
        # Highscores abrufen
        self.highscores = load_highscores()
        self.top_score = get_top_score()
        print(f"Aktueller Top-Score: {self.top_score['score']} von {self.top_score['name']}")
        
        # Lock-Delay-Variablen
        self.lock_delay = 400  # 0,4 Sekunden (von 250 auf 400 ms geändert)
        self.lock_timer = 0    # Timer für den Lock-Delay
        self.piece_landed = False  # Flag ob das Teil gelandet ist

    def try_rotation(self):
        """Verbesserte Rotation mit Wall-Kicks für Spielbarkeit"""
        # Normale Rotation versuchen
        if self.valid_move(self.current_piece, rotation=1):
            self.current_piece.rotation += 1
            # Wenn gelandet und erfolgreich rotiert, Lock-Timer zurücksetzen
            if self.piece_landed:
                self.lock_timer = 0
        else:
            # Wall-Kicks: Versuche nach links/rechts zu verschieben und zu rotieren
            old_rotation = self.current_piece.rotation
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
            # Für I-Tetromino besondere Behandlung (braucht mehr Platz)
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
        """Tauscht aktuelles Tetromino mit gehaltenem oder speichert es"""
        if not self.can_hold:
            return
            
        if self.held_piece:
            # Tausche aktuelles und gehaltenes Stück
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            # Position zurücksetzen
            self.current_piece.x = self.width // 2 - 2
            self.current_piece.y = 0
            self.current_piece.rotation = 0
        else:
            # Erstes Mal halten
            self.held_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            
        self.can_hold = False  # Blockiere bis neues Stück erscheint
        self.piece_landed = False
        self.lock_timer = 0

    def new_piece(self):
        # Zufällige Tetromino-Form auswählen
        shape = random.choice(SHAPES)
        # Tetromino in der Mitte oben erstellen
        return Tetromino(self.width // 2 - 2, 0, shape)
    
    def valid_move(self, piece, x_offset=0, y_offset=0, rotation=0):
        # Temporäre Rotation für die Überprüfung
        temp_rotation = (piece.rotation + rotation) % len(piece.shape)
        form = piece.shape[temp_rotation]
        
        for i, line in enumerate(form):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'O':
                    x = piece.x + j + x_offset
                    y = piece.y + i + y_offset
                    
                    # Überprüfen, ob außerhalb des Spielfelds
                    if x < 0 or x >= self.width or y >= self.height:
                        return False
                    # Überprüfen, ob Kollision mit anderen Blöcken
                    if y >= 0 and self.grid[y][x] != BLACK:
                        return False
        return True
    
    def clear_lines(self):
        lines_to_clear = []
        for i in range(self.height):
            if BLACK not in self.grid[i]:
                lines_to_clear.append(i)
            
        # Punkte basierend auf der Anzahl der gelöschten Zeilen vergeben
        if len(lines_to_clear) == 1:
            self.score += 40 * (self.level + 1)
        elif len(lines_to_clear) == 2:
            self.score += 100 * (self.level + 1)
        elif len(lines_to_clear) == 3:
            self.score += 300 * (self.level + 1)
        elif len(lines_to_clear) == 4:
            self.score += 1200 * (self.level + 1)
        
        # Zeilen löschen und von oben neue leere Zeilen einfügen
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [BLACK for _ in range(self.width)])
        
        self.lines_cleared += len(lines_to_clear)
        old_level = self.level
        self.level = self.lines_cleared // 10
        
        # Geschwindigkeit pro Level anpassen, aber nicht zu schnell werden
        if self.level > old_level:
            self.current_fall_speed = max(50, 250 - (self.level * 30))  # Stärkere Beschleunigung
            print(f"Level up! Neues Level: {self.level}, Geschwindigkeit: {self.current_fall_speed}")
    
    def get_shadow_piece(self):
        """Erstellt ein Schatten-Tetromino, das zeigt, wo der Block landen wird"""
        if self.game_over:
            return None
            
        shadow_piece = Tetromino(self.current_piece.x, self.current_piece.y, self.current_piece.shape)
        shadow_piece.rotation = self.current_piece.rotation
        
        # Bewege den Schatten so weit nach unten wie möglich
        while self.valid_move(shadow_piece, y_offset=1):
            shadow_piece.y += 1
            
        return shadow_piece
    
    def lock_piece(self):
        # Überprüfen, ob die Blöcke den oberen Rand berühren
        top_blocked = False
        for pos in self.current_piece.get_positions():
            x, y = pos
            # Wenn ein Block im unsichtbaren Bereich des Spielfelds ist
            if y < 0:
                top_blocked = True
                break
        
        for pos in self.current_piece.get_positions():
            x, y = pos
            if y >= 0:  # Nur wenn der Block im sichtbaren Bereich ist
                self.grid[y][x] = self.current_piece.color
        
        # Zeilen löschen, wenn sie voll sind
        self.clear_lines()
        
        # Nächstes Stück wird aktuelles Stück
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True  # Hold wieder erlauben
        self.piece_landed = False
        self.lock_timer = 0
        
        # Überprüfen, ob das Spiel vorbei ist
        # Game Over nur, wenn ein neuer Block nicht platziert werden kann oder der obere Rand blockiert ist
        if top_blocked or not self.valid_move(self.current_piece):
            self.game_over = True
            
            # Highscore aktualisieren wenn höher als bisheriger persönlicher Highscore oder Top 10
            is_top_10 = False
            if not self.highscores or self.score > self.highscores[-1]["score"] or len(self.highscores) < 10:
                is_top_10 = True
                
            if is_top_10:
                print(f"Neuer Highscore für {self.player_name}: {self.score}")
                save_success = save_highscore(self.player_name, self.score)
                if not save_success:
                    print("Fehler: Highscore konnte nicht gespeichert werden!")
                # Highscores neu laden
                self.highscores = load_highscores()

# Zeichenfunktionen
def draw_grid(screen, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                screen, 
                grid[i][j], 
                (PLAY_X + j * GRID_SIZE, PLAY_Y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                0
            )
            # Gitterlinien zeichnen
            pygame.draw.rect(
                screen, 
                GRAY, 
                (PLAY_X + j * GRID_SIZE, PLAY_Y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                1
            )

def draw_piece(screen, piece, is_shadow=False):
    """Zeichnet ein Tetromino mit 3D-Effekt"""
    if piece is None:
        return
        
    for pos in piece.get_positions():
        x, y = pos
        if y >= 0:  # Nur zeichnen, wenn der Block im sichtbaren Bereich ist
            color = LIGHT_GRAY if is_shadow else piece.color
            border_color = GRAY if is_shadow else (255, 255, 255)
            
            rect = (PLAY_X + x * GRID_SIZE, PLAY_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            if is_shadow:
                # Für Schatten nur einen Rahmen zeichnen
                pygame.draw.rect(screen, color, rect, 1)
            else:
                # Block mit 3D-Effekt zeichnen
                pygame.draw.rect(screen, color, rect, 0)
                
                # Innere Highlights für 3D-Effekt
                highlight_rect = (rect[0] + 1, rect[1] + 1, rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in color), highlight_rect, 1)
                
                # Rahmen zeichnen
                pygame.draw.rect(screen, border_color, rect, 1)

def draw_next_piece(screen, piece):
    font = pygame.font.Font(None, 30)
    label = font.render("Next:", True, WHITE)
    screen.blit(label, (WIDTH - 150, 100))
    
    # Position für das nächste Stück
    next_x = WIDTH - 150
    next_y = 150
    
    form = piece.shape[0]  # Erste Rotation des nächsten Stücks
    for i, line in enumerate(form):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'O':
                rect = (next_x + j * GRID_SIZE, next_y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, piece.color, rect, 0)
                
                # Innere Highlights für 3D-Effekt
                highlight_rect = (rect[0] + 1, rect[1] + 1, rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in piece.color), highlight_rect, 1)
                
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_held_piece(screen, piece):
    """Zeichnet das gehaltene Tetromino"""
    if piece is None:
        return
        
    font = pygame.font.Font(None, 30)
    label = font.render("Hold:", True, WHITE)
    screen.blit(label, (30, 200))
    
    hold_x = 30
    hold_y = 240
    
    form = piece.shape[0]  # Erste Rotation
    for i, line in enumerate(form):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'O':
                rect = (hold_x + j * GRID_SIZE, hold_y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, piece.color, rect, 0)
                
                # Innere Highlights für 3D-Effekt
                highlight_rect = (rect[0] + 1, rect[1] + 1, rect[2] - 2, rect[3] - 2)
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in piece.color), highlight_rect, 1)
                
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_score(screen, score, level, lines, player_name):
    font = pygame.font.Font(None, 30)
    
    player_text = font.render(f"Player: {player_name}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lines_text = font.render(f"Lines: {lines}", True, WHITE)
    
    screen.blit(player_text, (30, 70))
    screen.blit(score_text, (30, 100))
    screen.blit(level_text, (30, 130))
    screen.blit(lines_text, (30, 160))
    
    # Tastatur-Hilfe
    help_text = font.render("F: Full Screen  P: Pause  ESC: Titel", True, GRAY)
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 30))

def draw_highscores(screen, highscores, x, y, title="Highscores", show_date=True):
    # Überschrift
    title_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 24)
    
    title_text = title_font.render(title, True, YELLOW)
    screen.blit(title_text, (x, y))
    
    y += 40
    
    # Spaltenüberschriften
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
    
    # Keine Highscores vorhanden
    if not highscores:
        no_scores = text_font.render("No highscores yet!", True, GRAY)
        screen.blit(no_scores, (x + 70, y))
        return
    
    # Highscores anzeigen (maximal 10)
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
    # Halbtransparenter Hintergrund
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200))
    screen.blit(s, (0, 0))
    
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    font_button = pygame.font.Font(None, 28)
    
    game_over_text = font_big.render("GAME OVER", True, RED)
    player_text = font_small.render(f"Player: {player_name}", True, WHITE)
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    
    # Schatten-Effekt für Game Over Text
    shadow_offset = 3
    game_over_shadow = font_big.render("GAME OVER", True, (100, 0, 0))
    screen.blit(game_over_shadow, (WIDTH // 2 - game_over_text.get_width() // 2 + shadow_offset, 
                             100 + shadow_offset))
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 100))
    screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, 180))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 220))
    
    # Highscores anzeigen
    draw_highscores(screen, highscores, WIDTH // 2 - 200, 270, "Top Scores", False)
    
    # Buttons erstellen
    button_width = 220
    button_height = 50
    button_y = HEIGHT - 180
    button_spacing = 20
    
    restart_button = Button(
        WIDTH // 2 - button_width - button_spacing, button_y,
        button_width, button_height, 
        "Weiterspielen (R)", (0, 100, 0), (0, 150, 0)
    )
    
    new_profile_button = Button(
        WIDTH // 2 + button_spacing, button_y,
        button_width, button_height, 
        "Neues Profil (N)", (0, 0, 100), (0, 0, 150)
    )
    
    exit_button = Button(
        WIDTH // 2 - button_width // 2, button_y + button_height + button_spacing,
        button_width, button_height, 
        "Beenden (ESC)", (100, 0, 0), (150, 0, 0)
    )
    
    # Mausposition abrufen und Buttons aktualisieren
    mouse_pos = pygame.mouse.get_pos()
    restart_button.update(mouse_pos)
    new_profile_button.update(mouse_pos)
    exit_button.update(mouse_pos)
    
    # Buttons zeichnen
    restart_button.draw(screen, font_button)
    new_profile_button.draw(screen, font_button)
    exit_button.draw(screen, font_button)
    
    return restart_button, new_profile_button, exit_button

def draw_pause_screen(screen):
    # Halbtransparenter Hintergrund
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))
    
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    pause_text = font_big.render("PAUSED", True, CYAN)
    continue_text = font_small.render("Press P to Continue", True, WHITE)
    
    # Schatten-Effekt für Pause Text
    shadow_offset = 3
    pause_shadow = font_big.render("PAUSED", True, (0, 50, 80))
    screen.blit(pause_shadow, (WIDTH // 2 - pause_text.get_width() // 2 + shadow_offset, 
                         HEIGHT // 2 - 50 + shadow_offset))
    
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 30))

def toggle_fullscreen(screen):
    global fullscreen_mode
    
    if not fullscreen_mode:
        print("Wechsel zum Vollbildmodus")
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w, info.current_h
        
        try:
            # Echter Vollbildmodus mit nativer Auflösung für Schärfe
            screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
            fullscreen_mode = True
            # Bildschirmvariablen aktualisieren für zentriertes HUD
            update_display_variables(screen_w, screen_h)
        except Exception as e:
            print(f"Fehler beim Wechsel zum Vollbildmodus: {e}")
            # Fallback-Methode
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
    
    # Event-Queue leeren nach dem Moduswechsel
    pygame.event.clear()
    
    return screen

def name_input_screen(screen):
    font_big = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    
    title_text = font_big.render("TETRIS", True, CYAN)
    input_text = font_medium.render("Enter Your Name:", True, WHITE)
    hint_text = font_small.render("(Press ENTER when done)", True, GRAY)
    
    # Textbox für die Namenseingabe
    name_input = TextInput(WIDTH // 2 - 150, HEIGHT // 2, 300, font_medium)
    
    # Highscores laden
    highscores = load_highscores()
    
    running = True
    while running:
        screen.fill(BLACK)
        
        # Tetris-Logo mit Schatten
        shadow_offset = 3
        title_shadow = font_big.render("TETRIS", True, BLUE)
        screen.blit(title_shadow, (WIDTH // 2 - title_text.get_width() // 2 + shadow_offset, 
                                 100 + shadow_offset))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Namenseingabe-Texte
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 - 20))
        
        # Textbox aktualisieren und zeichnen
        name_input.update()
        name_input.draw(screen)
        
        # Highscores anzeigen
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
            
            # Prüfen, ob Enter gedrückt wurde
            if name_input.handle_event(event):
                player_name = name_input.text.strip()
                if not player_name:  # Falls kein Name eingegeben wird
                    player_name = "Player"
                return player_name

def main(use_existing_player=False, existing_player_name=None):
    # Pygame initialisieren
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris')
    
    # Spielernamen eingeben lassen oder vorhandenen Namen verwenden
    if use_existing_player and existing_player_name:
        player_name = existing_player_name
    else:
        player_name = name_input_screen(screen)
    
    # Uhr für die Framerate
    clock = pygame.time.Clock()
    
    # Tetris-Spiel mit Spielername erstellen
    game = Tetris(10, 20, player_name)  # 10x20 Spielfeld
    
    # Variablen für das Fallen der Tetrominoes
    fall_time = 0
    last_time = pygame.time.get_ticks()
    
    # Game-Over-Buttons
    restart_button = None
    new_profile_button = None
    exit_button = None
    
    # Variablen für die Wiederholungsfunktion bei gedrückten Tasten
    key_repeat_time = 0
    key_repeat_delay = 150  # Millisekunden bis zur Wiederholung
    key_repeat_interval = 1000 // 7  # Millisekunden zwischen Wiederholungen (7 pro Sekunde)
    move_left = False
    move_right = False
    move_down = False
    
    # Hauptspielschleife
    running = True
    while running:
        # Hintergrund zeichnen
        screen.fill(BLACK)
        
        # Spielfeld-Rahmen zeichnen
        pygame.draw.rect(screen, WHITE, (PLAY_X - 2, PLAY_Y - 2, PLAY_WIDTH + 4, PLAY_HEIGHT + 4), 2)
        
        # Aktuelle Mausposition
        mouse_pos = pygame.mouse.get_pos()
        
        # Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.game_over:
                        running = False
                    else:
                        game.paused = not game.paused
                
                if not game.game_over and not game.paused:
                    # Normale Spielsteuerung
                    if event.key == pygame.K_LEFT:
                        # Initial sofort bewegen
                        if game.valid_move(game.current_piece, x_offset=-1):
                            game.current_piece.x -= 1
                            if game.piece_landed:
                                game.lock_timer = 0
                        move_left = True
                        key_repeat_time = 0
                        
                    elif event.key == pygame.K_RIGHT:
                        # Initial sofort bewegen
                        if game.valid_move(game.current_piece, x_offset=1):
                            game.current_piece.x += 1
                            if game.piece_landed:
                                game.lock_timer = 0
                        move_right = True
                        key_repeat_time = 0
                        
                    elif event.key == pygame.K_DOWN:
                        # Initial sofort bewegen
                        if game.valid_move(game.current_piece, y_offset=1):
                            game.current_piece.y += 1
                        move_down = True
                        key_repeat_time = 0
                        
                    elif event.key == pygame.K_UP:
                        game.try_rotation()
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while game.valid_move(game.current_piece, y_offset=1):
                            game.current_piece.y += 1
                        game.lock_piece()
                    elif event.key == pygame.K_c or event.key == pygame.K_LSHIFT:  # C oder Umschalt für Hold
                        game.hold_piece()
                    elif event.key == pygame.K_p:
                        game.paused = True
                elif event.key == pygame.K_p and game.paused:
                    game.paused = False
                elif game.game_over:
                    # Game Over Tastatursteuerung
                    if event.key == pygame.K_r:
                        # Weiterspielen mit gleichem Namen
                        game = Tetris(10, 20, player_name)
                        fall_time = 0
                        last_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_n:
                        # Neues Profil - Namenseingabe und Neustart
                        player_name = name_input_screen(screen)
                        game = Tetris(10, 20, player_name)
                        fall_time = 0
                        last_time = pygame.time.get_ticks()
                
                # Vollbildmodus-Umschaltung immer verfügbar
                if event.key == pygame.K_f:
                    screen = toggle_fullscreen(screen)
            
            # Tastenloslassen
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False
                elif event.key == pygame.K_DOWN:
                    move_down = False
            
            # Button-Klick-Events prüfen wenn Game Over
            if game.game_over:
                if restart_button and restart_button.is_clicked(event):
                    # Weiterspielen mit gleichem Namen
                    game = Tetris(10, 20, player_name)
                    fall_time = 0
                    last_time = pygame.time.get_ticks()
                elif new_profile_button and new_profile_button.is_clicked(event):
                    # Neues Profil - Namenseingabe und Neustart
                    player_name = name_input_screen(screen)
                    game = Tetris(10, 20, player_name)
                    fall_time = 0
                    last_time = pygame.time.get_ticks()
                elif exit_button and exit_button.is_clicked(event):
                    # Spiel beenden
                    running = False
        
        # Wenn Spiel pausiert, zeige Pausenmenü an
        if game.paused:
            draw_pause_screen(screen)
            pygame.display.update()
            clock.tick(60)
            continue
        
        # Aktuelle Zeit für frameunabhängige Bewegung
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time
        last_time = current_time
        
        # Kontinuierliche Tasteneingabe mit Verzögerung und gleichmäßigem Tempo
        if not game.game_over and not game.paused:
            # Bewegungswiederholung mit Timer
            if move_left or move_right or move_down:
                key_repeat_time += dt
                
                if key_repeat_time >= key_repeat_delay:
                    # Bewegung nach links
                    if move_left and game.valid_move(game.current_piece, x_offset=-1):
                        game.current_piece.x -= 1
                        if game.piece_landed:
                            game.lock_timer = 0
                    
                    # Bewegung nach rechts
                    if move_right and game.valid_move(game.current_piece, x_offset=1):
                        game.current_piece.x += 1
                        if game.piece_landed:
                            game.lock_timer = 0
                    
                    # Bewegung nach unten
                    if move_down and game.valid_move(game.current_piece, y_offset=1):
                        game.current_piece.y += 1
                    
                    # Timer zurücksetzen auf das Intervall statt auf 0
                    key_repeat_time = key_repeat_delay - key_repeat_interval
            
            # Prüfen, ob das Tetromino gelandet ist
            if not game.valid_move(game.current_piece, y_offset=1):
                game.piece_landed = True
                game.lock_timer += dt  # Lock-Timer erhöhen
                
                # Wenn Lock-Delay abgelaufen ist, Tetromino einrasten
                if game.lock_timer >= game.lock_delay:
                    game.lock_piece()
            else:
                # Wenn nicht gelandet, Timer zurücksetzen
                game.piece_landed = False
                game.lock_timer = 0
        
        # Fallzeit aktualisieren
        if not game.game_over:
            fall_time += dt
            
            # Automatisches Fallen der Tetrominoes
            if fall_time >= game.current_fall_speed:
                fall_time = 0
                if game.valid_move(game.current_piece, y_offset=1):
                    game.current_piece.y += 1
                # Nicht sofort einrasten - wird durch den Lock-Delay gesteuert
        
        # Spielfeld zeichnen
        draw_grid(screen, game.grid)
        
        # Schatten des aktuellen Stücks zeichnen
        if not game.game_over:
            shadow_piece = game.get_shadow_piece()
            draw_piece(screen, shadow_piece, is_shadow=True)
        
        # Aktuelles Stück zeichnen
        if not game.game_over:
            draw_piece(screen, game.current_piece)
        
        # Nächstes Stück zeichnen
        draw_next_piece(screen, game.next_piece)
        
        # Gehaltenes Stück zeichnen
        draw_held_piece(screen, game.held_piece)
        
        # Punktestand zeichnen
        draw_score(screen, game.score, game.level, game.lines_cleared, game.player_name)
        
        # Game Over Bildschirm
        if game.game_over:
            restart_button, new_profile_button, exit_button = draw_game_over(
                screen, game.score, game.player_name, game.highscores
            )
            
            # Buttons bei Mausbewegung aktualisieren
            restart_button.update(mouse_pos)
            new_profile_button.update(mouse_pos)
            exit_button.update(mouse_pos)
        
        # Bildschirm aktualisieren
        pygame.display.update()
        
        # Framerate auf 60 FPS begrenzen
        clock.tick(60)
    
    # Spiel beenden
    pygame.quit()
    sys.exit()

# Startpunkt des Programms
if __name__ == "__main__":
    main()
