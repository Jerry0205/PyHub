import pygame
import sys
import math
import random
import time
import platform

try:
    import numpy as np
except ImportError:
    print("Numpy wird benötigt. Bitte installiere es mit: pip install numpy")
    sys.exit(1)

# Farben definieren
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

# Spielfeldgröße definieren
ROW_COUNT = 6
COLUMN_COUNT = 7

# Verhältnisse und Basiswerte
BASE_CELL_SIZE = 100  # Basis-Zellgröße
MENU_RATIO = 0.30     # Verhältnis vom Menü zur Gesamtbreite - erhöht für mehr Platz

# Button-Klasse für Benutzeroberfläche
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.active = False
        self.base_font_size = 24
        
    def draw(self, screen, scale_factor=1.0):
        # Skalierte Schriftgröße berechnen
        font_size = int(self.base_font_size * scale_factor)
        font = pygame.font.SysFont("Arial", font_size)
        
        # Farbauswahl basierend auf Hover- und Aktiv-Status
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
            
        # Button mit Schatten zeichnen
        shadow_rect = self.rect.copy()
        shadow_rect.x += max(4, int(4 * scale_factor))
        shadow_rect.y += max(4, int(4 * scale_factor))
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=12)
        
        # Hauptbutton
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, border_color, self.rect, width=border_width, border_radius=12)
        
        # Text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, clicked):
        return self.rect.collidepoint(pos) and clicked
        
    def set_active(self, active):
        self.active = active
        
    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    def set_size(self, width, height):
        center_x = self.rect.centerx
        center_y = self.rect.centery
        self.rect.width = width
        self.rect.height = height
        self.rect.centerx = center_x
        self.rect.centery = center_y

class GameUI:
    def __init__(self):
        # Spielkonstanten
        self.row_count = ROW_COUNT
        self.column_count = COLUMN_COUNT
        self.board = self.create_board()
        
        # Spielvariablen
        self.game_over = False
        self.game_mode = None  # 'koop' oder 'ai'
        self.difficulty = None
        self.current_player = 1
        self.score_player1 = 0
        self.score_player2 = 0
        self.winner = None
        self.falling_chip = None
        self.hover_col = None  # Für Vorschau-Anzeige
        
        # Bildschirm-Setup
        pygame.init()
        self.fullscreen = False
        self.base_width = 1024
        self.base_height = 768
        self.screen = pygame.display.set_mode((self.base_width, self.base_height), pygame.RESIZABLE)
        pygame.display.set_caption('Vier Gewinnt')
        
        # Größenberechnung
        self.calculate_sizes()
        
        # Buttons initialisieren
        self.init_buttons()
        
        # Clock für konstante Framerate
        self.clock = pygame.time.Clock()
        
    def calculate_sizes(self):
        # Aktuelle Bildschirmgröße
        self.width, self.height = self.screen.get_size()
        
        # Spielfeld nimmt 70% der Breite ein (größer als vorher)
        self.game_width = int(self.width * 0.7)
        self.menu_width = self.width - self.game_width
        
        # Zellengröße basierend auf verfügbarem Spielbereich
        self.cell_size_width = self.game_width // self.column_count
        self.cell_size_height = self.height // (self.row_count + 1)
        self.cell_size = min(self.cell_size_width, self.cell_size_height)
        
        # Skalierungsfaktor
        self.scale_factor = max(0.5, self.cell_size / BASE_CELL_SIZE)
        
        # Radius der Spielsteine
        self.chip_radius = int(self.cell_size * 0.4)
        
        # Spielfeldbreite und -position berechnen
        self.board_width = self.column_count * self.cell_size
        
        # Horizontale Zentrierung des Spielfelds
        self.board_offset_x = (self.game_width - self.board_width) // 2
        
        # Menübereich beginnt rechts vom Spielbereich
        self.menu_start_x = self.game_width
        
        # Zeichenbereich
        self.board_rect = pygame.Rect(
            self.board_offset_x, self.cell_size, 
            self.board_width, self.row_count * self.cell_size
        )
        self.menu_rect = pygame.Rect(self.menu_start_x, 0, self.menu_width, self.height)
        
    def init_buttons(self):
        # Basiswerte für Buttons
        self.button_width = int(min(220, self.menu_width * 0.85) * self.scale_factor)
        self.button_height = int(50 * self.scale_factor)
        self.button_spacing = int(60 * self.scale_factor)
        self.button_x = self.menu_start_x + (self.menu_width - self.button_width) // 2
        self.button_start_y = int(200 * self.scale_factor)
        
        # Spielmodus-Buttons
        self.koop_button = Button(self.button_x, self.button_start_y, 
                                  self.button_width, self.button_height, 
                                  "Koop Modus", GRAY, WHITE)
        
        self.ai_button = Button(self.button_x, self.button_start_y + self.button_spacing, 
                                self.button_width, self.button_height, 
                                "Gegen KI", GRAY, WHITE)
        
        # Schwierigkeitsgrad-Buttons
        self.easy_button = Button(self.button_x, self.button_start_y + self.button_spacing*2, 
                                 self.button_width, self.button_height, 
                                 "Leicht", GRAY, WHITE)
        
        self.medium_button = Button(self.button_x, self.button_start_y + self.button_spacing*3, 
                                   self.button_width, self.button_height, 
                                   "Mittel", GRAY, WHITE)
        
        self.hard_button = Button(self.button_x, self.button_start_y + self.button_spacing*4, 
                                 self.button_width, self.button_height, 
                                 "Schwer", GRAY, WHITE)
        
        self.unbeatable_button = Button(self.button_x, self.button_start_y + self.button_spacing*5, 
                                       self.button_width, self.button_height, 
                                       "Unschlagbar", GRAY, WHITE)
        
        # Reset-Button
        self.reset_button = Button(self.button_x, self.button_start_y + self.button_spacing*6, 
                                  self.button_width, self.button_height, 
                                  "Spiel neu starten", GRAY, WHITE)
        
        # Vollbild-Button
        self.fullscreen_button = Button(self.button_x, self.button_start_y + self.button_spacing*7, 
                                       self.button_width, self.button_height, 
                                       "Vollbild", GREEN, WHITE)
        
        # Beenden-Button
        self.exit_button = Button(self.button_x, self.button_start_y + self.button_spacing*8, 
                                 self.button_width, self.button_height, 
                                 "Spiel beenden", LIGHT_RED, WHITE, WHITE)
        
        # Gruppieren der Buttons
        self.difficulty_buttons = [self.easy_button, self.medium_button, 
                                 self.hard_button, self.unbeatable_button]
        
        self.all_buttons = [self.koop_button, self.ai_button] + self.difficulty_buttons + [
            self.reset_button, self.fullscreen_button, self.exit_button]
    
    def update_ui_positions(self):
        """Aktualisiert alle UI-Elemente nach einer Größenänderung"""
        self.calculate_sizes()
        
        # Buttons aktualisieren
        self.button_width = int(min(220, self.menu_width * 0.85) * self.scale_factor)
        self.button_height = int(50 * self.scale_factor)
        self.button_spacing = int(60 * self.scale_factor)
        self.button_x = self.menu_start_x + (self.menu_width - self.button_width) // 2
        self.button_start_y = int(200 * self.scale_factor)
        
        # Positionen und Größen aller Buttons aktualisieren
        for i, button in enumerate(self.all_buttons):
            button.set_position(self.button_x, self.button_start_y + i * self.button_spacing)
            button.set_size(self.button_width, self.button_height)
    
    def exit_game(self):
        """Beendet das Spiel vollständig"""
        pygame.quit()
        sys.exit()
    
    def create_board(self):
        """Erstellt ein leeres Spielfeld"""
        return np.zeros((self.row_count, self.column_count))
    
    def drop_piece(self, row, col, piece):
        """Lässt einen Spielstein in das Spielfeld fallen"""
        self.board[row][col] = piece
    
    def is_valid_location(self, col):
        """Prüft, ob ein Zug in der ausgewählten Spalte möglich ist"""
        col = int(col)  # Sicherstellen, dass col ein Integer ist
        return 0 <= col < self.column_count and self.board[self.row_count - 1][col] == 0
    
    def get_next_open_row(self, col):
        """Findet die nächste freie Zeile in einer Spalte"""
        col = int(col)  # Sicherstellen, dass col ein Integer ist
        for r in range(self.row_count):
            if self.board[r][col] == 0:
                return r
        return -1
    
    def winning_move(self, piece):
        """Prüft, ob der aktuelle Spieler gewonnen hat"""
        # Horizontale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(self.row_count):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True
    
        # Vertikale Überprüfung
        for c in range(self.column_count):
            for r in range(self.row_count - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True
    
        # Positive diagonale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(self.row_count - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True
    
        # Negative diagonale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(3, self.row_count):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True
                    
        return False
    
    def is_board_full(self):
        """Prüft, ob das Spielfeld voll ist"""
        return all(self.board[self.row_count-1][c] != 0 for c in range(self.column_count))
    
    def reset_game(self):
        """Setzt das Spiel zurück"""
        self.board = self.create_board()
        self.game_over = False
        self.current_player = 1
        self.winner = None
        self.falling_chip = None
    
    def toggle_fullscreen(self):
        """Wechselt zwischen Vollbild- und Fenstermodus"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Speichere vorherige Größe für Rückkehr zum Fenstermodus
            self.windowed_size = self.screen.get_size()
            
            # Umschalten ins Vollbild
            if platform.system() == 'Linux':
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Zurück zum Fenstermodus mit vorheriger Größe
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        # UI-Elemente an neue Größe anpassen
        self.update_ui_positions()
    
    def start_chip_animation(self, col, player):
        """Startet die Animation eines fallenden Spielsteins"""
        col = int(col)  # Sicherstellen, dass col ein Integer ist
        row = self.get_next_open_row(col)
        if row >= 0:
            self.falling_chip = {
                'col': col,
                'row': row,
                'player': player,
                'x': self.board_offset_x + col * self.cell_size + self.cell_size // 2,
                'y': self.cell_size // 2,
                'target_y': (self.row_count - row) * self.cell_size + self.cell_size // 2,
                'velocity': 0,
                'gravity': 0.7 * self.scale_factor,
                'bounces': 0,
                'done': False
            }
    
    def update_falling_chip(self):
        """Aktualisiert die Position eines fallenden Spielsteins"""
        if not self.falling_chip:
            return False
        
        chip = self.falling_chip
        
        # Physik update
        chip['velocity'] += chip['gravity']
        chip['y'] += chip['velocity']
        
        # Prüfen, ob Zielposition erreicht wurde
        if chip['y'] >= chip['target_y']:
            # Abprallen
            chip['y'] = chip['target_y']
            chip['velocity'] *= -0.5  # Abpralleffekt
            chip['bounces'] += 1
            
            # Nach ein paar Abprallern anhalten
            if chip['bounces'] > 2 or abs(chip['velocity']) < 1:
                # Animation beenden und Spielstein platzieren
                self.drop_piece(chip['row'], chip['col'], chip['player'])
                
                # Prüfen, ob der Spieler gewonnen hat
                if self.winning_move(chip['player']):
                    self.winner = chip['player']
                    self.game_over = True
                    if chip['player'] == 1:
                        self.score_player1 += 1
                    else:
                        self.score_player2 += 1
                # Prüfen, ob das Brett voll ist (Unentschieden)
                elif self.is_board_full():
                    self.game_over = True
                    self.winner = None
                else:
                    # Spielerwechsel
                    self.current_player = 2 if self.current_player == 1 else 1
                
                # Animation ist fertig
                self.falling_chip = None
                return True
        
        return False
    
    def evaluate_window(self, window, piece):
        """Bewertet ein 4er-Fenster für die KI"""
        opponent = 1 if piece == 2 else 2
        
        # Perfekte Bewertungslogik
        if window.count(piece) == 4:
            return 100  # Gewinn
        elif window.count(piece) == 3 and window.count(0) == 1:
            return 10   # Drei in einer Reihe
        elif window.count(piece) == 2 and window.count(0) == 2:
            return 2    # Zwei in einer Reihe
        
        # Defensive Bewertung - stark priorisiert
        if window.count(opponent) == 3 and window.count(0) == 1:
            return -80  # Hohe Priorität für Blockieren
        elif window.count(opponent) == 2 and window.count(0) == 2 and self.difficulty == "Unschlagbar":
            return -3   # Frühes Blockieren bei Unschlagbar-Modus
            
        return 0
        
    def score_position(self, board, piece):
        """Bewertet eine Spielposition mit perfekter Strategie"""
        score = 0
        opponent = 1 if piece == 2 else 2
        
        # Zentrumsgewichtung (entscheidend in Connect-4)
        center_column = self.column_count // 2
        center_array = [int(i) for i in list(board[:, center_column])]
        center_count = center_array.count(piece)
        score += center_count * 6  # Starke Gewichtung der Mittelspalte
        
        # Horizontale Bewertung
        for r in range(self.row_count):
            row_array = [int(i) for i in list(board[r,:])]
            
            # Bewerte alle möglichen 4-er Fenster
            for c in range(self.column_count - 3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)
        
        # Vertikale Bewertung
        for c in range(self.column_count):
            col_array = [int(i) for i in list(board[:,c])]
            
            for r in range(self.row_count - 3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece) * 1.2  # Stärkere Gewichtung für Vertikale
        
        # Diagonale Bewertung
        # Positive Diagonale (\)
        for r in range(self.row_count - 3):
            for c in range(self.column_count - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece) * 1.1
        
        # Negative Diagonale (/)
        for r in range(3, self.row_count):
            for c in range(self.column_count - 3):
                window = [board[r-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece) * 1.1
        
        # Vermeidung von "Trap"-Situationen
        # Scanne nach potenziellen Fallen, wo der Gegner 2 Gewinnmöglichkeiten hätte
        if self.difficulty == "Unschlagbar":
            for c in range(self.column_count):
                for r in range(self.row_count):
                    if board[r][c] == 0:  # Leeres Feld
                        # Prüfe, ob hier ein Stein fallen würde
                        if r == 0 or board[r-1][c] != 0:
                            b_copy = board.copy()
                            b_copy[r][c] = opponent
                            
                            # Zähle potenzielle Gewinnmöglichkeiten des Gegners
                            win_threats = 0
                            for test_col in range(self.column_count):
                                if self.get_next_open_row_for_board(b_copy, test_col) != -1:
                                    test_row = self.get_next_open_row_for_board(b_copy, test_col)
                                    test_board = b_copy.copy()
                                    test_board[test_row][test_col] = opponent
                                    if self.check_win_on_board(test_board, opponent):
                                        win_threats += 1
                            
                            # Stark negative Bewertung für Positionen, die mehrere Gewinnmöglichkeiten zulassen
                            if win_threats >= 2:
                                score -= 100
        
        return score
    
    def get_next_open_row_for_board(self, board, col):
        """Findet die nächste freie Zeile auf einem Board"""
        col = int(col)  # Sicherstellen, dass col ein Integer ist
        for r in range(self.row_count):
            if board[r][col] == 0:
                return r
        return -1
        
    def check_win_on_board(self, board, piece):
        """Prüft, ob ein Spieler auf einem bestimmten Brett gewonnen hat"""
        # Horizontale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(self.row_count):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True
    
        # Vertikale Überprüfung
        for c in range(self.column_count):
            for r in range(self.row_count - 3):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True
    
        # Positive diagonale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(self.row_count - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True
    
        # Negative diagonale Überprüfung
        for c in range(self.column_count - 3):
            for r in range(3, self.row_count):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True
                    
        return False
        
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """Verbesserter Minimax-Algorithmus für eine perfekte KI"""
        try:
            valid_locations = [c for c in range(self.column_count) if self.get_next_open_row_for_board(board, c) != -1]
            
            # Tiefenbegrenzung für bessere Performance
            if depth > 5:
                depth = 5
            
            # Prüfe auf Endzustände
            if self.check_win_on_board(board, 2):  # KI gewinnt
                return (None, 1000000 + depth)  # Je früher der Sieg, desto besser
            elif self.check_win_on_board(board, 1):  # Spieler gewinnt
                return (None, -1000000 - depth)  # Je später die Niederlage, desto besser
            elif len(valid_locations) == 0 or depth == 0:  # Unentschieden oder maximale Tiefe
                return (None, self.score_position(board, 2))
            
            # Optimierte Spaltenreihenfolge - zuerst zentrale Spalten testen für besseres Alpha-Beta-Pruning
            middle = self.column_count // 2
            # Sortiere nach Nähe zur Mitte (wichtig für optimale Connect-4-Strategie)
            valid_locations.sort(key=lambda x: abs(x - middle))
            
            if maximizing_player:  # KI (Spieler 2)
                value = -math.inf
                column = valid_locations[0] if valid_locations else None
                
                for col in valid_locations:
                    row = self.get_next_open_row_for_board(board, col)
                    if row == -1:
                        continue
                        
                    b_copy = board.copy()
                    b_copy[row][col] = 2
                    
                    # Direkter Gewinn in diesem Zug?
                    if self.check_win_on_board(b_copy, 2):
                        return (col, 1000000 + depth)  # Sofortiger Gewinn
                        
                    # Rekursiver Aufruf
                    new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                    if new_score > value:
                        value = new_score
                        column = col
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break  # Alpha-Beta-Pruning
                        
                return column, value
            
            else:  # Min-Spieler (Spieler 1)
                value = math.inf
                column = valid_locations[0] if valid_locations else None
                
                for col in valid_locations:
                    row = self.get_next_open_row_for_board(board, col)
                    if row == -1:
                        continue
                        
                    b_copy = board.copy()
                    b_copy[row][col] = 1
                    
                    # Rekursiver Aufruf
                    new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                    if new_score < value:
                        value = new_score
                        column = col
                    beta = min(beta, value)
                    if alpha >= beta:
                        break  # Alpha-Beta-Pruning
                        
                return column, value
        except Exception as e:
            print(f"Fehler im Minimax: {e}")
            # Fallback: zufällige gültige Spalte
            if valid_locations:
                return random.choice(valid_locations), 0
            return None, 0
    
    def ai_make_move(self):
        """KI berechnet ihren Zug und führt ihn aus"""
        if self.game_mode != 'ai' or self.current_player != 2 or self.game_over:
            return
        
        # Zeit für visuelle Wahrnehmung geben
        pygame.time.delay(300)  # Reduziert für schnellere Reaktion
        
        try:
            # Verfügbare Spalten ermitteln
            valid_columns = [c for c in range(self.column_count) if self.is_valid_location(c)]
            if not valid_columns:
                return
            
            # KI-Strategien basierend auf Schwierigkeitsgrad
            if self.difficulty == "Leicht":
                # 60% Chance auf einen intelligenten Zug, 40% Chance auf einen zufälligen Zug
                if random.random() > 0.4:
                    # Prüfe, ob KI in einem Zug gewinnen kann
                    for col in valid_columns:
                        row = self.get_next_open_row(col)
                        temp_board = self.board.copy()
                        temp_board[row][col] = 2
                        if self.check_win_on_board(temp_board, 2):
                            self.start_chip_animation(col, 2)
                            return
                    
                    # Blockiere gelegentlich gegnerische Gewinnzüge (70% Chance)
                    if random.random() > 0.3:
                        for col in valid_columns:
                            row = self.get_next_open_row(col)
                            temp_board = self.board.copy()
                            temp_board[row][col] = 1
                            if self.check_win_on_board(temp_board, 1):
                                self.start_chip_animation(col, 2)
                                return
                
                # Zufälliger Zug
                col = random.choice(valid_columns)
                self.start_chip_animation(col, 2)
                
            elif self.difficulty == "Mittel":
                # Prüfe, ob KI in einem Zug gewinnen kann
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return
                
                # Blockiere gegnerische Gewinnzüge
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return
                
                # Bevorzuge mittlere Spalten
                center_columns = [c for c in valid_columns 
                                 if c >= self.column_count//3 and c <= 2*self.column_count//3]
                if center_columns:
                    col = random.choice(center_columns)
                else:
                    col = random.choice(valid_columns)
                
                self.start_chip_animation(col, 2)
                
            elif self.difficulty == "Schwer":
                # Prüfe, ob KI in einem Zug gewinnen kann
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return
                
                # Blockiere gegnerische Gewinnzüge
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return
                
                # Minimax-Algorithmus mit moderater Tiefe (3)
                col, _ = self.minimax(self.board.copy(), 3, -math.inf, math.inf, True)
                if col is not None:
                    self.start_chip_animation(col, 2)
                else:
                    # Fallback: zufällige Spalte
                    self.start_chip_animation(random.choice(valid_columns), 2)
                    
            elif self.difficulty == "Unschlagbar":
                # Prüfe auf direkten Gewinn zuerst - absolute Priorität
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 2
                    if self.check_win_on_board(temp_board, 2):
                        self.start_chip_animation(col, 2)
                        return
                    
                # Blockiere Spielergewinn - zweithöchste Priorität
                for col in valid_columns:
                    row = self.get_next_open_row(col)
                    temp_board = self.board.copy()
                    temp_board[row][col] = 1
                    if self.check_win_on_board(temp_board, 1):
                        self.start_chip_animation(col, 2)
                        return
                
                # Optimierte Tiefe je nach Spielfortschritt
                move_count = np.count_nonzero(self.board)
                
                if move_count < 10:
                    depth = 5  # Frühe Spielphase
                elif move_count < 25:
                    depth = 4  # Mittlere Spielphase
                else:
                    depth = 3  # Späte Spielphase
                
                col, _ = self.minimax(self.board.copy(), depth, -math.inf, math.inf, True)
                
                if col is not None and self.is_valid_location(col):
                    self.start_chip_animation(col, 2)
                else:
                    # Fallback: bevorzuge mittlere Spalten
                    center_columns = [c for c in valid_columns if abs(c - self.column_count//2) <= 1]
                    if center_columns:
                        self.start_chip_animation(random.choice(center_columns), 2)
                    else:
                        self.start_chip_animation(random.choice(valid_columns), 2)
            else:
                # Fallback: zufällige Spalte
                self.start_chip_animation(random.choice(valid_columns), 2)
        except Exception as e:
            print(f"Fehler beim KI-Zug: {e}")
            # Fallback: zufällige Spalte
            valid_columns = [c for c in range(self.column_count) if self.is_valid_location(c)]
            if valid_columns:
                self.start_chip_animation(random.choice(valid_columns), 2)
    
    def draw(self):
        """Zeichnet das gesamte Spielfeld und die UI"""
        # Hintergrund
        self.screen.fill(BLACK)
        
        # Menubereich
        pygame.draw.rect(self.screen, DARK_GRAY, self.menu_rect)
        
        # Klare Trennung zwischen Spielfeld und Menü
        pygame.draw.line(self.screen, WHITE, 
                        (self.menu_start_x, 0), 
                        (self.menu_start_x, self.height), 
                        width=2)
        
        # Spielfeldrahmen
        pygame.draw.rect(self.screen, DARK_BLUE, self.board_rect, border_radius=15)
        
        # Zeichne das Spielfeld
        for c in range(self.column_count):
            for r in range(self.row_count):
                # Position der Zelle
                rect_x = self.board_offset_x + c * self.cell_size
                rect_y = (r + 1) * self.cell_size
                
                # Zeichne blaue Zelle
                pygame.draw.rect(self.screen, BLUE, 
                                (rect_x, rect_y, self.cell_size, self.cell_size))
                
                # Zeichne schwarzes Loch
                pygame.draw.circle(self.screen, BLACK,
                                  (rect_x + self.cell_size//2, rect_y + self.cell_size//2),
                                  self.chip_radius)
        
        # Zeichne die Spielsteine
        for c in range(self.column_count):
            for r in range(self.row_count):
                # Position zum Zeichnen berechnen
                center_x = self.board_offset_x + c * self.cell_size + self.cell_size//2
                center_y = (self.row_count - r) * self.cell_size + self.cell_size//2
                
                if self.board[r][c] == 1:  # Roter Spielstein
                    # Schatten
                    pygame.draw.circle(self.screen, DARK_RED, 
                                      (center_x + 3, center_y + 3), 
                                      self.chip_radius)
                    # Stein
                    pygame.draw.circle(self.screen, RED, 
                                      (center_x, center_y), 
                                      self.chip_radius)
                    
                    # Glanzeffekt
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100), 
                                      (highlight_size//2, highlight_size//2), 
                                      highlight_size//2)
                    self.screen.blit(highlight_surf, 
                                    (center_x - highlight_size//2, center_y - highlight_size//2))
                    
                elif self.board[r][c] == 2:  # Gelber Spielstein
                    # Schatten
                    pygame.draw.circle(self.screen, DARK_YELLOW, 
                                      (center_x + 3, center_y + 3), 
                                      self.chip_radius)
                    # Stein
                    pygame.draw.circle(self.screen, YELLOW, 
                                      (center_x, center_y), 
                                      self.chip_radius)
                    
                    # Glanzeffekt
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100), 
                                      (highlight_size//2, highlight_size//2), 
                                      highlight_size//2)
                    self.screen.blit(highlight_surf, 
                                    (center_x - highlight_size//2, center_y - highlight_size//2))
        
        # Fallender Spielstein
        if self.falling_chip:
            chip = self.falling_chip
            color = RED if chip['player'] == 1 else YELLOW
            shadow_color = DARK_RED if chip['player'] == 1 else DARK_YELLOW
            
            # Schatten
            pygame.draw.circle(self.screen, shadow_color, 
                              (chip['x'] + 3, chip['y'] + 3), 
                              self.chip_radius)
            # Stein
            pygame.draw.circle(self.screen, color, 
                              (chip['x'], chip['y']), 
                              self.chip_radius)
            
            # Glanzeffekt
            highlight_size = self.chip_radius // 2
            highlight_surf = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
            pygame.draw.circle(highlight_surf, (255, 255, 255, 100), 
                              (highlight_size//2, highlight_size//2), 
                              highlight_size//2)
            self.screen.blit(highlight_surf, 
                            (chip['x'] - highlight_size//2, chip['y'] - highlight_size//2))
        
        # Schwebeeffekt und Vorschau-Anzeige über dem Spielfeld
        if not self.game_over and self.game_mode and not self.falling_chip:
            mouse_pos = pygame.mouse.get_pos()
            
            # Nur im Spielfeldbereich anzeigen und nicht über Menü
            if (self.board_offset_x <= mouse_pos[0] < self.board_offset_x + self.board_width):
                rel_x = mouse_pos[0] - self.board_offset_x
                col = int(rel_x // self.cell_size)
                
                if 0 <= col < self.column_count:
                    # Schwebender Stein oben
                    x_pos = self.board_offset_x + col * self.cell_size + self.cell_size // 2
                    
                    color = RED if self.current_player == 1 else YELLOW
                    shadow_color = DARK_RED if self.current_player == 1 else DARK_YELLOW
                    
                    # Schatten
                    pygame.draw.circle(self.screen, shadow_color, 
                                      (x_pos + 3, self.cell_size//2 + 3), 
                                      self.chip_radius)
                    # Hauptkreis
                    pygame.draw.circle(self.screen, color, 
                                      (x_pos, self.cell_size//2), 
                                      self.chip_radius)
                    
                    # Glanzeffekt
                    highlight_size = self.chip_radius // 2
                    highlight_surf = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surf, (255, 255, 255, 100), 
                                      (highlight_size//2, highlight_size//2), 
                                      highlight_size//2)
                    self.screen.blit(highlight_surf, 
                                    (x_pos - highlight_size//2, self.cell_size//2 - highlight_size//2))
                    
                    # Vorschau: Zeige, wo der Spielstein landen würde
                    row = self.get_next_open_row(col)
                    if row != -1:  # Nur anzeigen, wenn Spalte nicht voll ist
                        # Position berechnen, wo der Stein landen würde
                        preview_y = (self.row_count - row) * self.cell_size + self.cell_size // 2
                        
                        # Transparenter Stein an Zielposition
                        preview_surf = pygame.Surface((self.chip_radius*2, self.chip_radius*2), pygame.SRCALPHA)
                        pygame.draw.circle(preview_surf, (color[0], color[1], color[2], 100), 
                                          (self.chip_radius, self.chip_radius), 
                                          self.chip_radius)
                        self.screen.blit(preview_surf, 
                                        (x_pos - self.chip_radius, preview_y - self.chip_radius))
        
        # Zeichne das Menü
        self.draw_menu()
        
        # Zeichne Buttons
        for button in self.all_buttons:
            button.draw(self.screen, self.scale_factor)
        
        # Gewinnermeldung
        if self.game_over:
            self.draw_win_message()
        
        # Bildschirmupdate
        pygame.display.update()
    
    def draw_menu(self):
        """Zeichnet das Menü mit Spielstand und Spielmodus"""
        font_size = int(32 * self.scale_factor)
        small_font_size = int(24 * self.scale_factor)
        
        title_font = pygame.font.SysFont("Arial", font_size, bold=True)
        font = pygame.font.SysFont("Arial", small_font_size)
        
        menu_center_x = self.menu_start_x + self.menu_width // 2
        
        # Titel mit Hintergrund
        title_y = 40 * self.scale_factor
        title = title_font.render("VIER GEWINNT", True, WHITE)
        title_rect = title.get_rect(center=(menu_center_x, title_y))
        
        # Hintergrund für den Titel
        title_bg = title_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (20, 20, 80), title_bg, border_radius=8)
        pygame.draw.rect(self.screen, LIGHT_BLUE, title_bg, width=2, border_radius=8)
        
        self.screen.blit(title, title_rect)
        
        # Trennlinie
        line_y = 70 * self.scale_factor
        pygame.draw.line(self.screen, GRAY, 
                         (self.menu_start_x + 20, line_y), 
                         (self.menu_start_x + self.menu_width - 20, line_y), 
                         max(2, int(2 * self.scale_factor)))
        
        # Spielstand-Überschrift
        score_title = font.render("Spielstand", True, WHITE)
        score_rect = score_title.get_rect(center=(menu_center_x, 100 * self.scale_factor))
        self.screen.blit(score_title, score_rect)
        
        # Punktestände
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
        
        # Wenn ein Spielmodus aktiv ist, zeige ihn über dem Spielfeld an (nicht hinter den Buttons)
        if self.game_mode:
            mode_text = "Koop-Modus" if self.game_mode == "koop" else "Gegen KI"
            difficulty_text = f" ({self.difficulty})" if self.game_mode == "ai" and self.difficulty else ""
            
            # Spielmodus-Text über dem Spielfeld
            status_text = mode_text + difficulty_text
            status_font = pygame.font.SysFont("Arial", int(24 * self.scale_factor))
            status = status_font.render(status_text, True, WHITE)
            
            # Positionierung oben mittig über dem Spielfeld
            status_rect = status.get_rect(center=(self.board_offset_x + self.board_width // 2, 20))
            
            # Hintergrund für besseren Kontrast
            bg_rect = status_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (20, 20, 40), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, LIGHT_BLUE, bg_rect, width=1, border_radius=5)
            
            # Text anzeigen
            self.screen.blit(status, status_rect)
    
    def draw_win_message(self):
        """Zeichnet die Gewinnermeldung oder Unentschieden-Nachricht"""
        font_size = int(32 * self.scale_factor)
        small_font_size = int(24 * self.scale_factor)
        
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        small_font = pygame.font.SysFont("Arial", small_font_size)
        
        if self.winner:
            # Gewinnerfarbe und -nachricht
            color = RED if self.winner == 1 else YELLOW
            player_name = "Spieler 1" if self.winner == 1 else ("Spieler 2" if self.game_mode == "koop" else "Computer")
            win_text = font.render(f"{player_name} gewinnt!", True, color)
            
            # Position berechnen (zentriert über dem Spielfeld)
            text_rect = win_text.get_rect(center=(self.board_offset_x + self.board_width // 2, self.cell_size // 2))
            
            # Hintergrund
            bg_rect = text_rect.inflate(50 * self.scale_factor, 30 * self.scale_factor)
            pygame.draw.rect(self.screen, DARK_GRAY, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, color, bg_rect, width=max(3, int(3 * self.scale_factor)), border_radius=15)
            
            # Text
            self.screen.blit(win_text, text_rect)
        else:
            # Unentschieden
            draw_text = font.render("Unentschieden!", True, WHITE)
            text_rect = draw_text.get_rect(center=(self.board_offset_x + self.board_width // 2, self.cell_size // 2))
            
            # Hintergrund
            bg_rect = text_rect.inflate(50 * self.scale_factor, 30 * self.scale_factor)
            pygame.draw.rect(self.screen, DARK_GRAY, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, bg_rect, width=max(3, int(3 * self.scale_factor)), border_radius=15)
            
            # Text
            self.screen.blit(draw_text, text_rect)
            
        # "Klicken für neues Spiel" Nachricht
        restart_text = small_font.render("Klicken für neues Spiel", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.board_offset_x + self.board_width // 2, self.cell_size // 2 + 40 * self.scale_factor))
        self.screen.blit(restart_text, restart_rect)
    
    def process_mouse_click(self, pos):
        """Verarbeitet Mausklicks auf das Spielfeld oder Buttons"""
        # Prüfen, ob Buttons geklickt wurden
        for i, button in enumerate(self.all_buttons):
            if button.is_clicked(pos, True):
                self.handle_button_click(i)
                return
        
        # Spielfeld-Klick (nur wenn Spiel läuft)
        if not self.game_over and self.game_mode and not self.falling_chip:
            # Prüfen, ob auf das Spielfeld geklickt wurde
            if (self.board_offset_x <= pos[0] < self.board_offset_x + self.board_width):
                col = int((pos[0] - self.board_offset_x) // self.cell_size)
                
                # Prüfen, ob der Spieler am Zug ist und der Zug gültig ist
                if (self.game_mode == 'koop' or (self.game_mode == 'ai' and self.current_player == 1)) and self.is_valid_location(col):
                    # Spielsteinanimation starten
                    self.start_chip_animation(col, self.current_player)
        
        # Wenn Spiel zu Ende ist, Neustart bei Klick auf das Spielfeld
        elif self.game_over and (self.board_offset_x <= pos[0] < self.board_offset_x + self.board_width):
            self.reset_game()
    
    def handle_button_click(self, button_index):
        """Verarbeitet Klicks auf verschiedene Buttons"""
        if button_index == 0:  # Koop Modus
            self.game_mode = 'koop'
            for button in self.difficulty_buttons:
                button.set_active(False)
            self.difficulty = None
            self.reset_game()
            
        elif button_index == 1:  # Gegen KI
            self.game_mode = 'ai'
            self.difficulty = None
            self.reset_game()
            
        elif 2 <= button_index <= 5:  # Schwierigkeitsgrad-Buttons
            if self.game_mode == 'ai':
                # Setze alle Schwierigkeitsgrad-Buttons zurück
                for i, button in enumerate(self.difficulty_buttons):
                    button.set_active(False)
                
                # Aktiviere ausgewählten Button
                self.difficulty_buttons[button_index - 2].set_active(True)
                
                # Setze Schwierigkeitsgrad
                difficulties = ["Leicht", "Mittel", "Schwer", "Unschlagbar"]
                self.difficulty = difficulties[button_index - 2]
                
                self.reset_game()
                
        elif button_index == 6:  # Spiel neu starten
            self.reset_game()
            
        elif button_index == 7:  # Vollbild
            self.toggle_fullscreen()
            
        elif button_index == 8:  # Spiel beenden
            self.exit_game()
    
    def run(self):
        """Hauptspielschleife"""
        while True:
            # Events verarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11 or event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and self.fullscreen:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and not self.fullscreen:
                        self.exit_game()  # ESC beendet das Spiel
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.process_mouse_click(pygame.mouse.get_pos())
                
                if event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        # Minimalgröße erzwingen
                        width, height = max(640, event.w), max(480, event.h)
                        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                        self.update_ui_positions()
                
                # Vorschau-Anzeige aktualisieren
                if event.type == pygame.MOUSEMOTION and not self.game_over and self.game_mode and not self.falling_chip:
                    mouse_pos = event.pos
                    if (self.board_offset_x <= mouse_pos[0] < self.board_offset_x + self.board_width):
                        rel_x = mouse_pos[0] - self.board_offset_x
                        self.hover_col = int(rel_x // self.cell_size)
                    else:
                        self.hover_col = None
            
            # Hover-Effekte für Buttons
            mouse_pos = pygame.mouse.get_pos()
            for button in self.all_buttons:
                button.check_hover(mouse_pos)
            
            # Update fallenden Chip
            if self.falling_chip:
                chip_landed = self.update_falling_chip()
                
                # Wenn KI am Zug ist und der Chip gelandet ist
                if chip_landed and self.game_mode == 'ai' and self.current_player == 2 and not self.game_over:
                    self.ai_make_move()
            
            # Zeichnen
            self.draw()
            
            # Framerate begrenzen
            self.clock.tick(60)

# Spiel starten
if __name__ == "__main__":
    try:
        game = GameUI()
        game.run()
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        pygame.quit()
        sys.exit(1)
