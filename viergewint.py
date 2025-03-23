import pygame
import sys
import math
import random
import time
import platform

# Versuche, numpy zu importieren – andernfalls wird eine Fehlermeldung ausgegeben.
try:
    import numpy as np
except ImportError:
    print("Numpy wird benötigt. Bitte installiere es mit: pip install numpy")
    sys.exit(1)

# Farben werden definiert.
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 180)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
YELLOW = (255, 255, 0)
DARK_YELLOW = (200, 200, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_BLUE = (100, 100, 255)
GREEN = (0, 200, 0)
LIGHT_RED = (255, 100, 100)  # Farbe für den Beenden-Button

# Spielfeldkonstanten: 6 Zeilen und 7 Spalten
ROW_COUNT = 6
COLUMN_COUNT = 7

# Basiswerte für das Skalieren des Spielfelds
BASE_CELL_SIZE = 100  # Basis-Zellgröße, dient als Referenz für den Skalierungsfaktor
MENU_RATIO = 0.30     # Verhältnis vom Menü zur Gesamtbreite

# -----------------------------------------------------------------------------
# Button-Klasse für die Benutzeroberfläche
# -----------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        # Der Button wird als Rechteck definiert und erhält initiale Eigenschaften
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False  # Gibt an, ob der Mauszeiger über dem Button schwebt
        self.active = False      # Für z.B. selektierte Buttons (z.B. Schwierigkeitsgrad)
        self.base_font_size = 24

    def draw(self, screen, scale_factor=1.0):
        # Berechne die skalierte Schriftgröße
        font_size = int(self.base_font_size * scale_factor)
        font = pygame.font.SysFont("Arial", font_size)

        # Farbe des Buttons ändert sich abhängig von Aktivität oder Hover-Status
        if self.active:
            current_color = self.hover_color
            border_color = self.text_color
            border_width = max(3, int(3 * scale_factor))
        elif self.is_hovered:
            current_color = self.hover_color
            border_color = BLACK
            border_width = max(2, int(2 * scale_factor))
        else:
            current_color = self.color
            border_color = BLACK
            border_width = max(2, int(2 * scale_factor))

        # Zeichne einen Schatten für den Button
        shadow_rect = self.rect.copy()
        shadow_rect.x += max(4, int(4 * scale_factor))
        shadow_rect.y += max(4, int(4 * scale_factor))
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=12)

        # Zeichne den Button selbst
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, border_color, self.rect, width=border_width, border_radius=12)

        # Zeichne den Buttontext
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        # Prüft, ob der Mauszeiger über dem Button schwebt
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, clicked):
        # Rückgabe True, wenn der Button angeklickt wurde
        return self.rect.collidepoint(pos) and clicked

    def set_active(self, active):
        self.active = active

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def set_size(self, width, height):
        # Die Größe des Buttons wird geändert – dabei bleibt das Zentrum gleich
        center_x = self.rect.centerx
        center_y = self.rect.centery
        self.rect.width = width
        self.rect.height = height
        self.rect.centerx = center_x
        self.rect.centery = center_y

# -----------------------------------------------------------------------------
# GameUI-Klasse: Enthält sämtliche Spiellogik und UI-Funktionen
# -----------------------------------------------------------------------------
class GameUI:
    def __init__(self):
        # Spielfeld-Konstanten: Anzahl Zeilen und Spalten
        self.row_count = ROW_COUNT
        self.column_count = COLUMN_COUNT
        self.board = self.create_board()

        # Spielvariablen
        self.game_over = False
        self.game_mode = None  # "koop" für Koop-Modus oder "ai" für KI-Modus
        self.difficulty = None
        self.current_player = 1  # 1 = Spieler 1 (Rot), 2 = Spieler 2 (Gelb / KI)
        self.score_player1 = 0
        self.score_player2 = 0
        self.winner = None
        self.falling_chip = None  # Wird genutzt, falls ein Chip animiert fällt
        self.hover_col = None     # Spalte für Vorschau-Anzeige beim Schweben der Maus

        # Initialisiere pygame und setze den Bildschirm
        pygame.init()

        # --- Vollbildmodus festlegen: ---
        # Das Spiel startet von Anfang an im Vollbildmodus, daher:
        self.fullscreen = True
        self.base_width = 1024  # Basiswerte (werden später skaliert)
        self.base_height = 768
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Vier Gewinnt")

        # Größenberechnung (z.B. Zellenbreiten, Offset etc.)
        self.calculate_sizes()

        # Buttons initialisieren – hier wird KEIN Vollbild-Button hinzugfügt.
        self.init_buttons()

        # Für konstante Framerate
        self.clock = pygame.time.Clock()

    def calculate_sizes(self):
        """Berechnet alle benötigten Größen und Positionen anhand der aktuellen Bildschirmgröße."""
        self.width, self.height = self.screen.get_size()

        # Das Spielfeld nimmt 70% der Breite ein
        self.game_width = int(self.width * 0.7)
        self.menu_width = self.width - self.game_width

        # Berechne die Größe einer Zelle
        self.cell_size_width = self.game_width // self.column_count
        self.cell_size_height = self.height // (self.row_count + 1)
        self.cell_size = min(self.cell_size_width, self.cell_size_height)

        # Berechne den Skalierungsfaktor relativ zur BASE_CELL_SIZE
        self.scale_factor = max(0.5, self.cell_size / BASE_CELL_SIZE)

        # Radius der Spielsteine (kugelförmig)
        self.chip_radius = int(self.cell_size * 0.4)

        # Gesamtbreite des Spielfelds und horizontale Zentrierung
        self.board_width = self.column_count * self.cell_size
        self.board_offset_x = (self.game_width - self.board_width) // 2

        # Menübereich beginnt rechts vom Spielfeld
        self.menu_start_x = self.game_width

        # Definition der Rechtecke für das Spielfeld und Menü
        self.board_rect = pygame.Rect(self.board_offset_x, self.cell_size,
                                      self.board_width,
                                      self.row_count * self.cell_size)
        self.menu_rect = pygame.Rect(self.menu_start_x, 0, self.menu_width, self.height)

    def init_buttons(self):
        """Initialisiert alle Buttons der Benutzeroberfläche (ohne Vollbild-Button)."""
        # Berechne die Basiswerte für Button-Größen und Positionen
        self.button_width = int(min(220, self.menu_width * 0.85) * self.scale_factor)
        self.button_height = int(50 * self.scale_factor)
        self.button_spacing = int(60 * self.scale_factor)
        self.button_x = self.menu_start_x + (self.menu_width - self.button_width) // 2
        self.button_start_y = int(200 * self.scale_factor)

        # Spielmodus-Buttons:
        self.koop_button = Button(self.button_x, self.button_start_y,
                                  self.button_width, self.button_height,
                                  "Koop Modus", GRAY, WHITE)

        self.ai_button = Button(self.button_x,
                                self.button_start_y + self.button_spacing,
                                self.button_width, self.button_height,
                                "Gegen KI", GRAY, WHITE)

        # Schwierigkeitsgrad-Buttons:
        self.easy_button = Button(self.button_x,
                                  self.button_start_y + self.button_spacing * 2,
                                  self.button_width, self.button_height,
                                  "Leicht", GRAY, WHITE)

        self.medium_button = Button(self.button_x,
                                    self.button_start_y + self.button_spacing * 3,
                                    self.button_width, self.button_height,
                                    "Mittel", GRAY, WHITE)

        self.hard_button = Button(self.button_x,
                                  self.button_start_y + self.button_spacing * 4,
                                  self.button_width, self.button_height,
                                  "Schwer", GRAY, WHITE)

        self.unbeatable_button = Button(self.button_x,
                                        self.button_start_y + self.button_spacing * 5,
                                        self.button_width, self.button_height,
                                        "Unschlagbar", GRAY, WHITE)

        # Reset-Button (zum Neustarten des Spiels)
        self.reset_button = Button(self.button_x,
                                   self.button_start_y + self.button_spacing * 6,
                                   self.button_width, self.button_height,
                                   "Spiel neu starten", GRAY, WHITE)

        # Beenden-Button (um das Spiel zu beenden)
        self.exit_button = Button(self.button_x,
                                  self.button_start_y + self.button_spacing * 7,
                                  self.button_width, self.button_height,
                                  "Spiel beenden", LIGHT_RED, WHITE, WHITE)

        # Alle Buttons werden in einer Liste zusammengefasst.
        # Der Vollbild-Button wurde entfernt, da das Spiel direkt im Vollbildmodus läuft.
        self.difficulty_buttons = [
            self.easy_button, self.medium_button,
            self.hard_button, self.unbeatable_button
        ]
        self.all_buttons = ([self.koop_button, self.ai_button]
                            + self.difficulty_buttons
                            + [self.reset_button, self.exit_button])

    def update_ui_positions(self):
        """Aktualisiert alle UI-Elemente nach einer Größenänderung."""
        self.calculate_sizes()

        self.button_width = int(min(220, self.menu_width * 0.85) * self.scale_factor)
        self.button_height = int(50 * self.scale_factor)
        self.button_spacing = int(60 * self.scale_factor)
        self.button_x = self.menu_start_x + (self.menu_width - self.button_width) // 2
        self.button_start_y = int(200 * self.scale_factor)

        # Aktualisiere Position und Größe aller Buttons gemäß dem neuen Skalierungsfaktor.
        for i, button in enumerate(self.all_buttons):
            button.set_position(self.button_x,
                                self.button_start_y + i * self.button_spacing)
            button.set_size(self.button_width, self.button_height)

    def exit_game(self):
        """Beendet das Spiel vollständig."""
        pygame.quit()
        sys.exit()

    def create_board(self):
        """Erstellt ein leeres Spielfeld als numpy-Array."""
        return np.zeros((self.row_count, self.column_count))

    def drop_piece(self, row, col, piece):
        """Fügt einen Spielstein (piece) in das Spielfeld ein."""
        self.board[row][col] = piece

    def is_valid_location(self, col):
        """Prüft, ob in der gewünschten Spalte noch Platz vorhanden ist."""
        col = int(col)  # Stelle sicher, dass col ein Integer ist.
        return (0 <= col < self.column_count and
                self.board[self.row_count - 1][col] == 0)

    def get_next_open_row(self, col):
        """Findet die allererste freie Zeile in der gewählten Spalte."""
        col = int(col)
        for r in range(self.row_count):
            if self.board[r][col] == 0:
                return r
        return -1

    def winning_move(self, piece):
        """Prüft, ob der übergebene Spielstein (piece) vier in einer Reihe hat."""
        # Horizontale Überprüfung:
        for c in range(self.column_count - 3):
            for r in range(self.row_count):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True

        # Vertikale Überprüfung:
        for c in range(self.column_count):
            for r in range(self.row_count - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True

        # Positive diagonale Überprüfung (\):
        for c in range(self.column_count - 3):
            for r in range(self.row_count - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True

        # Negative diagonale Überprüfung (/):
        for c in range(self.column_count - 3):
            for r in range(3, self.row_count):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True

        return False

    def is_board_full(self):
        """Gibt True zurück, wenn keine leere Zelle mehr vorhanden ist."""
        return all(self.board[self.row_count - 1][c] != 0
                   for c in range(self.column_count))

    def reset_game(self):
        """Setzt das Spiel zurück (leeres Spielfeld, Neustart etc.)."""
        self.board = self.create_board()
        self.game_over = False
        self.current_player = 1
        self.winner = None
        self.falling_chip = None

    def start_chip_animation(self, col, player):
        """
        Startet die Animation eines fallenden Spielsteins.
        Hier wird die Start- und Zielposition sowie die nötigen physikalischen
        Parameter (Schwerkraft, Geschwindigkeit etc.) definiert.
        """
        col = int(col)
        row = self.get_next_open_row(col)
        if row >= 0:
            self.falling_chip = {
                "col": col,
                "row": row,
                "player": player,
                "x": self.board_offset_x + col * self.cell_size +
                     self.cell_size // 2,
                "y": self.cell_size // 2,
                "target_y": (self.row_count - row) * self.cell_size +
                            self.cell_size // 2,
                "velocity": 0,
                "gravity": 0.7 * self.scale_factor,
                "bounces": 0,
                "done": False,
            }

    def update_falling_chip(self):
        """Aktualisiert die Position des fallenden Chips und prüft, ob er sein Ziel erreicht hat."""
        if not self.falling_chip:
            return False

        chip = self.falling_chip
        chip["velocity"] += chip["gravity"]
        chip["y"] += chip["velocity"]

        # Wenn der Chip sein Ziel erreicht hat, erfolgt ein Abprall-Effekt.
        if chip["y"] >= chip["target_y"]:
            chip["y"] = chip["target_y"]
            chip["velocity"] *= -0.5
            chip["bounces"] += 1

            # Nach einigen Abprallern wird der Chip festgesetzt.
            if chip["bounces"] > 2 or abs(chip["velocity"]) < 1:
                self.drop_piece(chip["row"], chip["col"], chip["player"])
                if self.winning_move(chip["player"]):
                    self.winner = chip["player"]
                    self.game_over = True
                    if chip["player"] == 1:
                        self.score_player1 += 1
                    else:
                        self.score_player2 += 1
                elif self.is_board_full():
                    self.game_over = True
                    self.winner = None
                else:
                    self.current_player = 2 if self.current_player == 1 else 1

                # Animation beenden:
                self.falling_chip = None
                return True

        return False

    def evaluate_window(self, window, piece):
        """
        Bewertet ein Fenster (Liste von 4 Zellen) für die KI.
        Je nachdem, wie viele gleiche Spielsteine (oder Gegner) im Fenster sind, wird ein Wert zurückgegeben.
        """
        opponent = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            return 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            return 10
        elif window.count(piece) == 2 and window.count(0) == 2:
            return 2

        if window.count(opponent) == 3 and window.count(0) == 1:
            return -80
        elif (window.count(opponent) == 2 and window.count(0) == 2 and
              self.difficulty == "Unschlagbar"):
            return -3

        return 0

    def score_position(self, board, piece):
        """
        Bewertet die gesamte Brettposition für den Spieler (piece) unter Anwendung verschiedener Strategien.
        Dazu gehören:
          - Gewichtung der zentralen Spalte,
          - horizontale, vertikale und diagonale Anordnungen,
          - Vermeiden von "Trap"-Situationen.
        """
        score = 0
        opponent = 1 if piece == 2 else 2

        # Starke Gewichtung der mittleren Spalte
        center_column = self.column_count // 2
        center_array = [int(i) for i in list(board[:, center_column])]
        center_count = center_array.count(piece)
        score += center_count * 6

        # Horizontale Bewertung
        for r in range(self.row_count):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(self.column_count - 3):
                window = row_array[c : c + 4]
                score += self.evaluate_window(window, piece)

        # Vertikale Bewertung mit etwas höherer Gewichtung
        for c in range(self.column_count):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(self.row_count - 3):
                window = col_array[r : r + 4]
                score += self.evaluate_window(window, piece) * 1.2

        # Positive Diagonale (\)
        for r in range(self.row_count - 3):
            for c in range(self.column_count - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece) * 1.1

        # Negative Diagonale (/)
        for r in range(3, self.row_count):
            for c in range(self.column_count - 3):
                window = [board[r - i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece) * 1.1

        # Prüfe zusätzliche Bedrohungen im "Unschlagbar"-Modus
        if self.difficulty == "Unschlagbar":
            for c in range(self.column_count):
                for r in range(self.row_count):
                    if board[r][c] == 0:
                        if r == 0 or board[r - 1][c] != 0:
                            b_copy = board.copy()
                            b_copy[r][c] = opponent
                            win_threats = 0
                            for test_col in range(self.column_count):
                                if self.get_next_open_row_for_board(b_copy, test_col) != -1:
                                    test_row = self.get_next_open_row_for_board(b_copy, test_col)
                                    test_board = b_copy.copy()
                                    test_board[test_row][test_col] = opponent
                                    if self.check_win_on_board(test_board, opponent):
                                        win_threats += 1
                            if win_threats >= 2:
                                score -= 100

        return score

    def get_next_open_row_for_board(self, board, col):
        """Ermittelt die nächste freie Zeile für ein gegebenes Board (wird in der KI genutzt)."""
        col = int(col)
        for r in range(self.row_count):
            if board[r][col] == 0:
                return r
        return -1

    def check_win_on_board(self, board, piece):
        """Prüft, ob ein Spieler (piece) auf einem bestimmten Board gewonnen hat."""
        for c in range(self.column_count - 3):
            for r in range(self.row_count):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True

        for c in range(self.column_count):
            for r in range(self.row_count - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True

        for c in range(self.column_count - 3):
            for r in range(self.row_count - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True

        for c in range(self.column_count - 3):
            for r in range(3, self.row_count):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True

        return False

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Führt den verbesserten Minimax-Algorithmus mit Alpha-Beta-Pruning aus.
        Diese Methode ermittelt den optimalen Zug für die KI.
        """
        try:
            valid_locations = [
                c
                for c in range(self.column_count)
                if self.get_next_open_row_for_board(board, c) != -1
            ]

            # Begrenze die Tiefe für Performancezwecke
            if depth > 5:
                depth = 5

            # Endzustände prüfen
            if self.check_win_on_board(board, 2):
                return (None, 1000000 + depth)
            elif self.check_win_on_board(board, 1):
                return (None, -1000000 - depth)
            elif len(valid_locations) == 0 or depth == 0:
                return (None, self.score_position(board, 2))

            # Sortiere die gültigen Spalten, sodass die mittleren Spalten zuerst geprüft werden.
            middle = self.column_count // 2
            valid_locations.sort(key=lambda x: abs(x - middle))

            if maximizing_player:
                value = -math.inf
                column = valid_locations[0] if valid_locations else None

                for col in valid_locations:
                    row = self.get_next_open_row_for_board(board, col)
                    if row == -1:
                        continue

                    b_copy = board.copy()
                    b_copy[row][col] = 2

                    if self.check_win_on_board(b_copy, 2):
                        return (col, 1000000 + depth)

                    new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                    if new_score > value:
                        value = new_score
                        column = col
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break

                return column, value
            else:
                value = math.inf
                column = valid_locations[0] if valid_locations else None

                for col in valid_locations:
                    row = self.get_next_open_row_for_board(board, col)
                    if row == -1:
                        continue

                    b_copy = board.copy()
                    b_copy[row][col] = 1

                    new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                    if new_score < value:
                        value = new_score
                        column = col
                    beta = min(beta, value)
                    if alpha >= beta:
                        break

                return column, value
        except Exception as e:
            print(f"Fehler im Minimax: {e}")
            if valid_locations:
                return random.choice(valid_locations), 0
            return None, 0

    def ai_make_move(self):
        """
        Lässt die KI einen Zug berechnen und ausführen.
        Hier werden je nach Schwierigkeitsgrad verschiedene Strategien angewandt.
        """
        if self.game_mode != "ai" or self.current_player != 2 or self.game_over:
            return

        # Kurze Verzögerung für visuelle Effekte
        pygame.time.delay(300)

        try:
            valid_columns = [c for c in range(self.column_count)
                             if self.is_valid_location(c)]
            if not valid_columns:
                return

            # Leichter Schwierigkeitsgrad: Mischung aus intelligenten und zufälligen Zügen.
            if self.difficulty == "Leicht":
                if random.random() > 0.4:
                    for col in valid_columns:
                        row = self.get_next_open_row(col)
                        temp_board = self.board.copy()
                        temp_board[row][col] = 2
                        if self.check_win_on_board(temp_board, 2):
                            self.start_chip_animation(col, 2)
                            return

                    if random.random() > 0.3:
                        for col in valid_columns:
                            row = self.get_next_open_row(col)
                            temp_board = self.board.copy()
                            temp_board[row][col] = 1
                            if self.check_win_on_board(temp_board, 1):
                                self.start_chip_animation(col, 2)
                                return

                col = random.choice(valid_columns)
                self.start_chip_animation(col, 2)
            # Mittlerer Schwierigkeitsgrad: Gewinne praktikabel selbst prüfen und blockieren.
            elif self.difficulty == "Mittel":
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return

                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return

                center_columns = [c for c in valid_columns
                                  if c >= self.column_count // 3 and
                                  c <= 2 * self.column_count // 3]
                if center_columns:
                    col = random.choice(center_columns)
                else:
                    col = random.choice(valid_columns)
                self.start_chip_animation(col, 2)
            # Schwerer Schwierigkeitsgrad: Mischung aus Gewinnprüfungen und Minimax.
            elif self.difficulty == "Schwer":
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return

                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return

                col, _ = self.minimax(self.board.copy(), 3, -math.inf,
                                      math.inf, True)
                if col is not None:
                    self.start_chip_animation(col, 2)
                else:
                    self.start_chip_animation(random.choice(valid_columns), 2)
            # Unschlagbar: höchste Priorität für Gewinne und Blockaden,
            # ggf. mit verschiedener Suchtiefe je nach Spielphase.
            elif self.difficulty == "Unschlagbar":
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return

                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return

                move_count = np.count_nonzero(self.board)
                if move_count < 10:
                    depth = 5
                elif move_count < 25:
                    depth = 4
                else:
                    depth = 3

                col, _ = self.minimax(self.board.copy(), depth,
                                      -math.inf, math.inf, True)
                if col is not None and self.is_valid_location(col):
                    self.start_chip_animation(col, 2)
                else:
                    center_columns = [c for c in valid_columns
                                      if abs(c - self.column_count // 2) <= 1]
                    if center_columns:
                        self.start_chip_animation(random.choice(center_columns), 2)
                    else:
                        self.start_chip_animation(random.choice(valid_columns), 2)
            else:
                self.start_chip_animation(random.choice(valid_columns), 2)
        except Exception as e:
            print(f"Fehler beim KI-Zug: {e}")
            valid_columns = [c for c in range(self.column_count)
                             if self.is_valid_location(c)]
            if valid_columns:
                self.start_chip_animation(random.choice(valid_columns), 2)

    def draw(self):
        """
        Zeichnet das komplette Spielfeld, die fallenden Chips, die Buttons
        und das Menü. Dieser Block beinhaltet auch alle visuellen Effekte.
        """
        # Hintergrund zeichnen
        self.screen.fill(BLACK)
        # Menübereich zeichnen
        pygame.draw.rect(self.screen, DARK_GRAY, self.menu_rect)
        # Trennlinie zwischen Spielfeld und Menü
        pygame.draw.line(self.screen, WHITE, (self.menu_start_x, 0),
                         (self.menu_start_x, self.height), width=2)
        # Spielfeldrahmen
        pygame.draw.rect(self.screen, DARK_BLUE, self.board_rect,
                         border_radius=15)

        # Zeichne das Raster (blaue Zellen mit schwarzem Kreis als "Loch")
        for c in range(self.column_count):
            for r in range(self.row_count):
                rect_x = self.board_offset_x + c * self.cell_size
                rect_y = (r + 1) * self.cell_size
                pygame.draw.rect(self.screen, BLUE,
                                 (rect_x, rect_y, self.cell_size, self.cell_size))
                pygame.draw.circle(self.screen, BLACK,
                                   (rect_x + self.cell_size // 2,
                                    rect_y + self.cell_size // 2),
                                   self.chip_radius)

        # Zeichne die bereits abgelegten Spielsteine
        for c in range(self.column_count):
            for r in range(self.row_count):
                center_x = (self.board_offset_x + c * self.cell_size +
                            self.cell_size // 2)
                center_y = ((self.row_count - r) * self.cell_size +
                            self.cell_size // 2)
                if self.board[r][c] == 1:
                    # Erster Spieler (Rot) inkl. Schatten und Glanzeffekt
                    pygame.draw.circle(self.screen, DARK_RED,
                                       (center_x + 3, center_y + 3),
                                       self.chip_radius)
                    pygame.draw.circle(self.screen, RED,
                                       (center_x, center_y), self.chip_radius)
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size),
                                                    pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100),
                                       (highlight_size // 2,
                                        highlight_size // 2),
                                       highlight_size // 2)
                    self.screen.blit(highlight_surf,
                                     (center_x - highlight_size // 2,
                                      center_y - highlight_size // 2))
                elif self.board[r][c] == 2:
                    # Zweiter Spieler (Gelb/Computer) inkl. Schatten und Glanzeffekt
                    pygame.draw.circle(self.screen, DARK_YELLOW,
                                       (center_x + 3, center_y + 3),
                                       self.chip_radius)
                    pygame.draw.circle(self.screen, YELLOW,
                                       (center_x, center_y), self.chip_radius)
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size),
                                                    pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100),
                                       (highlight_size // 2,
                                        highlight_size // 2),
                                       highlight_size // 2)
                    self.screen.blit(highlight_surf,
                                     (center_x - highlight_size // 2,
                                      center_y - highlight_size // 2))

        # Zeichne den fallenden Chip (während der Animation)
        if self.falling_chip:
            chip = self.falling_chip
            color = RED if chip["player"] == 1 else YELLOW
            shadow_color = DARK_RED if chip["player"] == 1 else DARK_YELLOW
            pygame.draw.circle(self.screen, shadow_color,
                               (chip["x"] + 3, chip["y"] + 3),
                               self.chip_radius)
            pygame.draw.circle(self.screen, color,
                               (chip["x"], chip["y"]),
                               self.chip_radius)
            highlight_size = self.chip_radius // 2
            highlight_surf = pygame.Surface((highlight_size, highlight_size),
                                            pygame.SRCALPHA)
            pygame.draw.circle(highlight_surf, (255, 255, 255, 100),
                               (highlight_size // 2, highlight_size // 2),
                               highlight_size // 2)
            self.screen.blit(highlight_surf,
                             (chip["x"] - highlight_size // 2,
                              chip["y"] - highlight_size // 2))

        # Falls das Spiel läuft und noch kein Chip animiert wird, 
        # wird die Vorschau des Spielsteins angezeigt:
        if not self.game_over and self.game_mode and not self.falling_chip:
            mouse_pos = pygame.mouse.get_pos()
            if (self.board_offset_x <= mouse_pos[0] <
                    self.board_offset_x + self.board_width):
                rel_x = mouse_pos[0] - self.board_offset_x
                col = int(rel_x // self.cell_size)
                if 0 <= col < self.column_count:
                    x_pos = self.board_offset_x + col * self.cell_size + self.cell_size // 2
                    color = RED if self.current_player == 1 else YELLOW
                    shadow_color = DARK_RED if self.current_player == 1 else DARK_YELLOW
                    pygame.draw.circle(self.screen, shadow_color,
                                       (x_pos + 3, self.cell_size // 2 + 3),
                                       self.chip_radius)
                    pygame.draw.circle(self.screen, color,
                                       (x_pos, self.cell_size // 2),
                                       self.chip_radius)
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size),
                                                    pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100),
                                       (highlight_size // 2, highlight_size // 2),
                                       highlight_size // 2)
                    self.screen.blit(highlight_surf,
                                     (x_pos - highlight_size // 2,
                                      self.cell_size // 2 - highlight_size // 2))
                    row = self.get_next_open_row(col)
                    if row != -1:
                        preview_y = (self.row_count - row) * self.cell_size + self.cell_size // 2
                        preview_surf = pygame.Surface((self.chip_radius * 2,
                                                       self.chip_radius * 2),
                                                      pygame.SRCALPHA)
                        pygame.draw.circle(preview_surf, (color[0], color[1], color[2], 100),
                                           (self.chip_radius, self.chip_radius),
                                           self.chip_radius)
                        self.screen.blit(preview_surf,
                                         (x_pos - self.chip_radius,
                                          preview_y - self.chip_radius))

        # Menü und Buttons zeichnen
        self.draw_menu()
        for button in self.all_buttons:
            button.draw(self.screen, self.scale_factor)

        # Wird eine Gewinn- oder Unentschieden-Nachricht angezeigt?
        if self.game_over:
            self.draw_win_message()
        pygame.display.update()

    def draw_menu(self):
        """
        Zeichnet das Menü. Dieses enthält den Titel, den Spielstand und den
        aktuellen Spielmodus inkl. (falls vorhanden) Schwierigkeitsgrad.
        """
        font_size = int(32 * self.scale_factor)
        small_font_size = int(24 * self.scale_factor)
        title_font = pygame.font.SysFont("Arial", font_size, bold=True)
        font = pygame.font.SysFont("Arial", small_font_size)
        menu_center_x = self.menu_start_x + self.menu_width // 2

        # Titel und Hintergrund
        title_y = 40 * self.scale_factor
        title = title_font.render("VIER GEWINNT", True, WHITE)
        title_rect = title.get_rect(center=(menu_center_x, title_y))
        title_bg = title_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (20, 20, 80), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, LIGHT_BLUE, title_bg, width=2, border_radius=8)
        self.screen.blit(title, title_rect)

        # Trennlinie unter dem Titel
        line_y = 70 * self.scale_factor
        pygame.draw.line(self.screen, GRAY,
                         (self.menu_start_x + 20, line_y),
                         (self.menu_start_x + self.menu_width - 20, line_y),
                         max(2, int(2 * self.scale_factor)))

        # Anzeige des Spielstands
        score_title = font.render("Spielstand", True, WHITE)
        score_rect = score_title.get_rect(center=(menu_center_x, 100 * self.scale_factor))
        self.screen.blit(score_title, score_rect)

        player1 = font.render(f"Spieler 1 (Rot): {self.score_player1}", True, RED)
        player1_rect = player1.get_rect(center=(menu_center_x, 135 * self.scale_factor))
        self.screen.blit(player1, player1_rect)

        player2 = font.render(f"Spieler 2 (Gelb): {self.score_player2}", True, YELLOW)
        player2_rect = player2.get_rect(center=(menu_center_x, 165 * self.scale_factor))
        self.screen.blit(player2, player2_rect)

        # Weitere Trennlinie
        line_y = 195 * self.scale_factor
        pygame.draw.line(self.screen, GRAY,
                         (self.menu_start_x + 20, line_y),
                         (self.menu_start_x + self.menu_width - 20, line_y),
                         max(2, int(2 * self.scale_factor)))

        # Anzeige des aktiven Spielmodus und ggf. Schwierigkeitsgrad,
        # falls ein Spielmodus aktiv ist.
        if self.game_mode:
            mode_text = "Koop-Modus" if self.game_mode == "koop" else "Gegen KI"
            difficulty_text = f" ({self.difficulty})" if (
                self.game_mode == "ai" and self.difficulty) else ""
            status_text = mode_text + difficulty_text
            status_font = pygame.font.SysFont("Arial", int(24 * self.scale_factor))
            status = status_font.render(status_text, True, WHITE)
            status_rect = status.get_rect(center=(self.board_offset_x + self.board_width // 2, 20))
            bg_rect = status_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (20, 20, 40), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, LIGHT_BLUE, bg_rect, width=1, border_radius=5)
            self.screen.blit(status, status_rect)

    def draw_win_message(self):
        """
        Zeichnet die Gewinn- oder Unentschieden-Nachricht.
        Zusätzlich wird ein Hinweis angezeigt, dass man durch Klicken
        ein neues Spiel starten kann.
        """
        font_size = int(32 * self.scale_factor)
        small_font_size = int(24 * self.scale_factor)
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        small_font = pygame.font.SysFont("Arial", small_font_size)

        if self.winner:
            color = RED if self.winner == 1 else YELLOW
            player_name = "Spieler 1" if self.winner == 1 else ("Spieler 2" if self.game_mode == "koop" else "Computer")
            win_text = font.render(f"{player_name} gewinnt!", True, color)
            text_rect = win_text.get_rect(center=(self.board_offset_x + self.board_width // 2,
                                                   self.cell_size // 2))
            bg_rect = text_rect.inflate(50 * self.scale_factor, 30 * self.scale_factor)
            pygame.draw.rect(self.screen, DARK_GRAY, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, color, bg_rect, width=max(3, int(3 * self.scale_factor)), border_radius=15)
            self.screen.blit(win_text, text_rect)
        else:
            draw_text = font.render("Unentschieden!", True, WHITE)
            text_rect = draw_text.get_rect(center=(self.board_offset_x + self.board_width // 2,
                                                   self.cell_size // 2))
            bg_rect = text_rect.inflate(50 * self.scale_factor, 30 * self.scale_factor)
            pygame.draw.rect(self.screen, DARK_GRAY, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, bg_rect, width=max(3, int(3 * self.scale_factor)), border_radius=15)
            self.screen.blit(draw_text, text_rect)

        restart_text = small_font.render("Klicken für neues Spiel", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.board_offset_x + self.board_width // 2,
                                                      self.cell_size // 2 + 40 * self.scale_factor))
        self.screen.blit(restart_text, restart_rect)

    def process_mouse_click(self, pos):
        """
        Verarbeitet den Mausklick.
        Zuerst wird geprüft, ob ein Button angeklickt wurde.
        Falls nicht, wird der Klick als Zug im Spielfeld gewertet.
        Bei Spielende wird durch Klick auf das Spielfeld das Spiel zurückgesetzt.
        """
        # Überprüfe, ob ein Button angeklickt wurde.
        for i, button in enumerate(self.all_buttons):
            if button.is_clicked(pos, True):
                self.handle_button_click(i)
                return

        # Wenn das Spiel läuft, verarbeite einen Klick im Spielfeld.
        if not self.game_over and self.game_mode and not self.falling_chip:
            if self.board_offset_x <= pos[0] < self.board_offset_x + self.board_width:
                col = int((pos[0] - self.board_offset_x) // self.cell_size)
                if ((self.game_mode == "koop") or 
                    (self.game_mode == "ai" and self.current_player == 1)
                   ) and self.is_valid_location(col):
                    self.start_chip_animation(col, self.current_player)
        # Bei Spielende: Klick im Spielfeld startet ein neues Spiel.
        elif self.game_over and (self.board_offset_x <= pos[0] < self.board_offset_x + self.board_width):
            self.reset_game()

    def handle_button_click(self, button_index):
        """
        Verarbeitet die Klicks auf die einzelnen Buttons.
        Hinweis: Da der Vollbild-Button entfernt wurde,
        entspricht der Buttonindex 7 nun dem "Spiel beenden"-Button.
        """
        if button_index == 0:  # Koop-Modus starten
            self.game_mode = "koop"
            for button in self.difficulty_buttons:
                button.set_active(False)
            self.difficulty = None
            self.reset_game()
        elif button_index == 1:  # Spiele gegen KI
            self.game_mode = "ai"
            self.difficulty = None
            self.reset_game()
        elif 2 <= button_index <= 5:  # Auswahl des Schwierigkeitsgrads
            if self.game_mode == "ai":
                for i, button in enumerate(self.difficulty_buttons):
                    button.set_active(False)
                self.difficulty_buttons[button_index - 2].set_active(True)
                difficulties = ["Leicht", "Mittel", "Schwer", "Unschlagbar"]
                self.difficulty = difficulties[button_index - 2]
                self.reset_game()
        elif button_index == 6:  # Spiel neu starten
            self.reset_game()
        elif button_index == 7:  # Spiel beenden
            self.exit_game()

    def run(self):
        """
        Hauptspielschleife.
        Hier werden Events verarbeitet (Maus, Tastatur, Fenstergrößenänderung).
        Zudem wird geprüft, ob Animationen (fallender Chip) laufen,
        ob die KI am Zug ist, und zuletzt wird das Spielfeld gezeichnet.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Bei Tastendrücken wird ESC zum Beenden genutzt.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.process_mouse_click(pygame.mouse.get_pos())

                # Fenstergrößenänderung (nur im Fenstermodus, hier aber nicht aktiv, da Vollbild)
                if event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        width, height = max(640, event.w), max(480, event.h)
                        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                        self.update_ui_positions()

                # Aktualisiere den Hover-Effekt, wenn sich die Maus bewegt.
                if (event.type == pygame.MOUSEMOTION and not self.game_over and 
                    self.game_mode and not self.falling_chip):
                    mouse_pos = event.pos
                    if self.board_offset_x <= mouse_pos[0] < self.board_offset_x + self.board_width:
                        rel_x = mouse_pos[0] - self.board_offset_x
                        self.hover_col = int(rel_x // self.cell_size)
                    else:
                        self.hover_col = None

            # Aktualisiere den Hover-Status aller Buttons
            mouse_pos = pygame.mouse.get_pos()
            for button in self.all_buttons:
                button.check_hover(mouse_pos)

            # Wenn ein Chip animiert fällt, aktualisiere seine Position.
            if self.falling_chip:
                chip_landed = self.update_falling_chip()
                # Falls die Animation beendet ist und die KI am Zug ist, führe KI-Zug aus.
                if chip_landed and self.game_mode == "ai" and self.current_player == 2 and not self.game_over:
                    self.ai_make_move()

            self.draw()
            self.clock.tick(60)

# -----------------------------------------------------------------------------
# Spielstart:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        game = GameUI()
        game.run()
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        pygame.quit()
        sys.exit(1)
