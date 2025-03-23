# Hauptimporte
import pygame
import subprocess
import os
import json
import sys

# Konfigurationskonstanten
HIGHLIGHT_COLOR = (0, 122, 255, 128)  # Farbe für Hervorhebungen
MENU_OPTIONS = [
    "2048",
    "Snake",
    "Pong",
    "4 Gewinnt",
    "Slots",
    "Tetris",
    "Beenden"
]  # Letzte Option beendet das Programm

# Erweiterte Einstellungsoptionen: Dark Mode, Credits, Key Bindings und Back
SETTINGS_OPTIONS = ["Dark Mode", "Credits", "Key Bindings", "Back"]


class GameLauncher:
    def __init__(self):
        # Initialisiert den Spielstarter mit Standardwerten
        self.screen_config = {
            "width": 0,  # Aktuelle Bildschirmbreite
            "height": 0,  # Aktuelle Bildschirmhöhe
            "surface": None,  # Pygame-Bildschirmoberfläche
            "fonts": {},  # Geladene Schriftarten
            "current_view": "main_menu",  # Ansichten: main_menu, settings, credits, key_bindings, secret_menu
            "settings": {"dark_mode": False},
        }

        # Zustandsvariablen für Mausinteraktion
        self.state = {
            "mouse_hover": -1,      # Überfahrener Menüpunkt (Maus)
            "settings_hover": False,  # Über Settings-Button schweben (Maus)
        }

        # Für das Key Bindings-Untermenü:
        # "list" zeigt die Liste der Spiele, "detail" die Keybinds zum ausgewählten Spiel.
        self.current_key_binding_view = "list"
        self.selected_game = None

        # Pfad zur config.json im selben Verzeichnis wie dieses Skript
        self.config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.json"
        )

        # Platzhalter für den unsichtbaren Secret-Button (im Hauptmenü)
        self.secret_button_rect = None

        self.init_pygame()    # Pygame initialisieren
        self.load_settings()  # Einstellungen laden
        self.update_fonts()   # Schriftarten aktualisieren
        self.load_assets()    # Assets (z.B. Logos) laden

    def init_pygame(self):
        pygame.init()
        info = pygame.display.Info()
        self.screen_config["width"] = info.current_w
        self.screen_config["height"] = info.current_h
        self.screen_config["surface"] = pygame.display.set_mode(
            (self.screen_config["width"], self.screen_config["height"]),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("PYHUB")

    def load_settings(self):
        try:
            with open(self.config_file, "r") as file:
                self.screen_config["settings"] = json.load(file)
        except FileNotFoundError:
            self.save_settings()

    def save_settings(self):
        with open(self.config_file, "w") as file:
            json.dump(self.screen_config["settings"], file)

    def update_fonts(self):
        h = self.screen_config["height"]
        self.screen_config["fonts"] = {
            "title": pygame.font.Font(None, h // 10),   # Titelschrift
            "option": pygame.font.Font(None, h // 15),    # Menüschrift
            "button": pygame.font.Font(None, h // 20),    # Buttonschrift
        }

    def load_assets(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            dark_logo_path = os.path.join(base_path, "assetes", "Logo.png")
            white_logo_path = os.path.join(base_path, "assetes", "Whitelogo.png")
            self.dark_logo = pygame.image.load(dark_logo_path).convert_alpha()
            self.white_logo = pygame.image.load(white_logo_path).convert_alpha()
            print("Logos erfolgreich geladen")
        except Exception as e:
            print("Error loading logos:", e)
            self.dark_logo = None
            self.white_logo = None

    def get_colors(self):
        dark = self.screen_config["settings"]["dark_mode"]
        return ((0, 0, 0) if dark else (255, 255, 255),  # Hintergrundfarbe
                (255, 255, 255) if dark else (0, 0, 0))    # Textfarbe

    def draw_highlight(self, rect):
        highlight = pygame.Surface(
            (rect.width + 30, rect.height + 20), pygame.SRCALPHA
        )
        pygame.draw.rect(
            highlight,
            HIGHLIGHT_COLOR,
            highlight.get_rect(),
            border_radius=5
        )
        self.screen_config["surface"].blit(highlight, (rect.x - 15, rect.y - 10))

    def draw_main_menu(self):
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)

        # Überschrift: Logo oder Titel
        current_logo = (
            self.dark_logo
            if self.screen_config["settings"]["dark_mode"]
            else self.white_logo
        )
        if current_logo is not None:
            logo_width = self.screen_config["width"] // 3.5
            logo_height = self.screen_config["height"] // 2.5
            logo_scaled = pygame.transform.scale(
                current_logo, (logo_width, logo_height)
            )
            logo_rect = logo_scaled.get_rect(
                center=(
                    self.screen_config["width"] // 2,
                    self.screen_config["height"] // 7,
                )
            )
            screen.blit(logo_scaled, logo_rect)
        else:
            title = self.screen_config["fonts"]["title"].render(
                "PYHUB", True, text_color
            )
            title_rect = title.get_rect(
                center=(
                    self.screen_config["width"] // 2,
                    self.screen_config["height"] // 8,
                )
            )
            screen.blit(title, title_rect)

        # Settings-Button (separat gezeichnet)
        button_text = "Settings"
        button_font = self.screen_config["fonts"]["button"]
        button_surf = button_font.render(button_text, True, text_color)
        button_rect = button_surf.get_rect(
            midleft=(
                self.screen_config["width"] // 2 + self.screen_config["width"] // 8,
                self.screen_config["height"] // 7,
            )
        )
        if self.state["settings_hover"]:
            self.draw_highlight(button_rect)
        screen.blit(button_surf, button_rect)

        # Menüoptionen zeichnen
        option_rects = []
        for i, option in enumerate(MENU_OPTIONS):
            font = self.screen_config["fonts"]["option"]
            option_surf = font.render(option, True, text_color)
            option_rect = option_surf.get_rect(
                center=(
                    self.screen_config["width"] // 2,
                    self.screen_config["height"] // 4 + 
                    i * (self.screen_config["height"] // 12),
                )
            )
            if i == self.state["mouse_hover"]:
                self.draw_highlight(option_rect)
            screen.blit(option_surf, option_rect)
            option_rects.append(option_rect)

        # Definiere den unsichtbaren Secret-Button unten rechts.
        # Er wird nicht gezeichnet und reagiert auch nicht auf Hover.
        self.secret_button_rect = pygame.Rect(
            self.screen_config["width"] - 60,
            self.screen_config["height"] - 60,
            50,
            50
        )

        pygame.display.flip()
        return option_rects, button_rect

    def draw_settings_menu(self):
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)

        title = self.screen_config["fonts"]["title"].render(
            "Settings", True, text_color
        )
        title_rect = title.get_rect(
            center=(self.screen_config["width"] // 2,
                    self.screen_config["height"] // 8)
        )
        screen.blit(title, title_rect)

        option_rects = []
        for i, option in enumerate(SETTINGS_OPTIONS):
            font = self.screen_config["fonts"]["option"]
            option_surf = font.render(option, True, text_color)
            option_rect = option_surf.get_rect(
                center=(
                    self.screen_config["width"] // 2,
                    self.screen_config["height"] // 4 +
                    i * (self.screen_config["height"] // 12),
                )
            )
            if i == self.state["mouse_hover"]:
                self.draw_highlight(option_rect)
            screen.blit(option_surf, option_rect)
            option_rects.append(option_rect)

        pygame.display.flip()
        return option_rects

    def draw_credits_menu(self):
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)
        width = self.screen_config["width"]
        height = self.screen_config["height"]

        title = self.screen_config["fonts"]["title"].render(
            "Credits", True, text_color
        )
        title_rect = title.get_rect(center=(width // 2, height // 8))
        screen.blit(title, title_rect)

        credits_lines = [
            "Entwickler: Brian Gollek, Jeremy Hundt,",
            "Nino Mrkwitschka, Petja Höllein, Conrad Schüler",
            "",
            "Version: 2.0",
            "",
            "Weitere Credits: Chatgpt 4o, Claude3.7, Deepseek"
        ]
        font = self.screen_config["fonts"]["option"]
        line_height = self.screen_config["height"] // 15
        start_y = self.screen_config["height"] // 4
        for i, line in enumerate(credits_lines):
            line_surf = font.render(line, True, text_color)
            line_rect = line_surf.get_rect(
                center=(width // 2, start_y + i * line_height)
            )
            screen.blit(line_surf, line_rect)

        back_text = "Back"
        back_surf = self.screen_config["fonts"]["button"].render(
            back_text, True, text_color
        )
        back_rect = back_surf.get_rect(
            center=(width // 2, height * 7 // 8)
        )
        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            self.draw_highlight(back_rect)
        screen.blit(back_surf, back_rect)

        pygame.display.flip()
        return [back_rect]

    def draw_key_bindings_list(self):
        """
        Zeichnet eine Spieleliste (mit größerem vertikalen Abstand) zur Auswahl
        eines Game für die Anzeige der zugehörigen Key Bindings.
        """
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)
        width = self.screen_config["width"]
        height = self.screen_config["height"]

        title = self.screen_config["fonts"]["title"].render(
            "Key Bindings", True, text_color
        )
        title_rect = title.get_rect(center=(width // 2, height // 8))
        screen.blit(title, title_rect)

        games = ["2048", "Snake", "Pong", "4 Gewinnt", "Slots", "Tetris"]
        option_rects = []
        font = self.screen_config["fonts"]["option"]
        for i, game in enumerate(games):
            option_surf = font.render(game, True, text_color)
            option_rect = option_surf.get_rect(
                center=(width // 2, height // 4 + i * (height // 10))
            )
            if i == self.state["mouse_hover"]:
                self.draw_highlight(option_rect)
            screen.blit(option_surf, option_rect)
            option_rects.append(option_rect)

        back_text = "Back"
        back_surf = self.screen_config["fonts"]["button"].render(
            back_text, True, text_color
        )
        back_rect = back_surf.get_rect(
            center=(width // 2, height * 7 // 8)
        )
        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            self.draw_highlight(back_rect)
        screen.blit(back_surf, back_rect)

        pygame.display.flip()
        return {"game_rects": option_rects, "back": back_rect}

    def draw_key_bindings_detail(self, game_name):
        """
        Zeichnet die Detailansicht der Key Bindings für ein ausgewähltes Spiel.
        Hier wurde der Zeilenabstand vergrößert.
        """
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)
        width = self.screen_config["width"]
        height = self.screen_config["height"]

        title_text = f"{game_name} Key Bindings"
        title = self.screen_config["fonts"]["title"].render(
            title_text, True, text_color
        )
        title_rect = title.get_rect(center=(width // 2, height // 8))
        screen.blit(title, title_rect)

        key_bindings = {
            "2048": [
                "Linke Pfeiltaste -> Bewegt die Kacheln nach links",
                "Rechte Pfeiltaste -> Bewegt die Kacheln nach rechts",
                "Obere Pfeiltaste -> Bewegt die Kacheln nach oben",
                "Untere Pfeiltaste -> Bewegt die Kacheln nach unten",
            ],
            "Snake": [
                "Linke Pfeiltaste -> Richtung nach links",
                "Rechte Pfeiltaste -> Richtung nach rechts",
                "Obere Pfeiltaste -> Richtung nach oben",
                "Untere Pfeiltaste -> Richtung nach unten",
            ],
            "Pong": [
                "Spieler 1: W -> Schläger hoch und S -> Schläger runter",
                "Spieler 2: Pfeil Oben -> Schläger hoch und Pfeil Unten -> Schläger runter",
                "ESC -> Menü / Beenden",
            ],
            "4 Gewinnt": [
                "Maus-Klick in die gewünschte Spalte -> Platziert den Chip",
            ],
            "Slots": [
                "Steuerung erfolgt über Buttons:",
                "  SPIN, BET, ALL-IN, KREDIT, ZURÜCKZAHLEN, BEENDEN",
            ],
            "Tetris": [
                "Linke Pfeiltaste  ->  Verschiebt Tetromino nach links",
                "Rechte Pfeiltaste  ->  Verschiebt Tetromino nach rechts",
                "Untere Pfeiltaste  ->  Soft Drop (schneller fallen)",
                "Obere Pfeiltaste  ->  Rotiert das Tetromino",
                "Leertaste  ->  Hard Drop (sofort absetzen)",
                "C oder Linke Umschalttaste  ->  Hold-Funktion",
                "ESC  ->  Pause / Menü",
                "F  ->  Vollbild bzw. Fenster",
            ]
        }
        lines = key_bindings.get(game_name, ["Keine Key Bindings vorhanden."])
        font = self.screen_config["fonts"]["option"]
        line_height = self.screen_config["height"] // 15
        start_y = self.screen_config["height"] // 4
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, text_color)
            line_rect = line_surf.get_rect(
                center=(width // 2, start_y + i * line_height)
            )
            screen.blit(line_surf, line_rect)

        back_text = "Back"
        back_surf = self.screen_config["fonts"]["button"].render(
            back_text, True, text_color
        )
        back_rect = back_surf.get_rect(
            center=(width // 2, height * 7 // 8)
        )
        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            self.draw_highlight(back_rect)
        screen.blit(back_surf, back_rect)

        pygame.display.flip()
        return [back_rect]

    def draw_secret_menu(self):
        """
        Zeichnet das Secret-Menü mit rotem Hintergrund und der Überschrift
        "UNFERTIG!!!!! alles noch in arbeit". Hier erscheinen vier Buttons:
          - "Mines": Startet mines.py
          - "Car": Startet car.py
          - "Race": Startet race.py
          - "Back": Kehrt zum Hauptmenü zurück.
        """
        screen = self.screen_config["surface"]
        # Roter Hintergrund
        screen.fill((255, 0, 0))
        white = (255, 255, 255)
        width = self.screen_config["width"]
        height = self.screen_config["height"]
        mouse_pos = pygame.mouse.get_pos()

        # Überschrift
        title_text = "UNFERTIG!!!!! alles noch in arbeit"
        title_surf = self.screen_config["fonts"]["title"].render(
            title_text, True, white
        )
        title_rect = title_surf.get_rect(center=(width // 2, int(height * 0.15)))
        screen.blit(title_surf, title_rect)

        button_font = self.screen_config["fonts"]["button"]

        # Mines-Button
        mines_text = "Mines"
        mines_surf = button_font.render(mines_text, True, white)
        mines_rect = mines_surf.get_rect(center=(width // 2, int(height * 0.35)))
        if mines_rect.collidepoint(mouse_pos):
            self.draw_highlight(mines_rect)
        screen.blit(mines_surf, mines_rect)

        # Car-Button
        car_text = "Car"
        car_surf = button_font.render(car_text, True, white)
        car_rect = car_surf.get_rect(center=(width // 2, int(height * 0.50)))
        if car_rect.collidepoint(mouse_pos):
            self.draw_highlight(car_rect)
        screen.blit(car_surf, car_rect)

        # Race-Button
        race_text = "Race"
        race_surf = button_font.render(race_text, True, white)
        race_rect = race_surf.get_rect(center=(width // 2, int(height * 0.65)))
        if race_rect.collidepoint(mouse_pos):
            self.draw_highlight(race_rect)
        screen.blit(race_surf, race_rect)

        # Back-Button
        back_text = "Back"
        back_surf = button_font.render(back_text, True, white)
        back_rect = back_surf.get_rect(center=(width // 2, int(height * 0.80)))
        if back_rect.collidepoint(mouse_pos):
            self.draw_highlight(back_rect)
        screen.blit(back_surf, back_rect)

        pygame.display.flip()
        return mines_rect, car_rect, race_rect, back_rect

    def handle_secret_menu_events(self, event, mines_rect, car_rect, race_rect, back_rect):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE,
            )
            self.update_fonts()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if mines_rect.collidepoint(pos):
                self.launch_mines()
            elif car_rect.collidepoint(pos):
                self.launch_car()
            elif race_rect.collidepoint(pos):
                self.launch_race()
            elif back_rect.collidepoint(pos):
                self.screen_config["current_view"] = "main_menu"

    def launch_mines(self):
        mines_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assetes", "miau", "mines.py"
        )
        if os.path.exists(mines_path):
            subprocess.run([sys.executable, mines_path])
        else:
            print("Error: mines.py not found!")

    def launch_car(self):
        car_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assetes", "miau", "car.py"
        )
        if os.path.exists(car_path):
            subprocess.run([sys.executable, car_path])
        else:
            print("Error: car.py not found!")

    def launch_race(self):
        race_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assetes", "miau", "race.py"
        )
        if os.path.exists(race_path):
            subprocess.run([sys.executable, race_path])
        else:
            print("Error: race.py not found!")

    def handle_key_bindings_events(self, event, rects_or_dict):
        if isinstance(rects_or_dict, dict):
            self.handle_key_bindings_list_events(event, rects_or_dict)
        elif isinstance(rects_or_dict, list):
            self.handle_key_bindings_detail_events(event, rects_or_dict)

    def handle_key_bindings_list_events(self, event, rects_dict):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE,
            )
            self.update_fonts()
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.state["mouse_hover"] = next(
                (i for i, r in enumerate(rects_dict["game_rects"]) if r.collidepoint(mouse_pos)),
                -1,
            )
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if rects_dict["back"].collidepoint(pos):
                self.screen_config["current_view"] = "settings"
                self.current_key_binding_view = "list"
                self.selected_game = None
            else:
                games = ["2048", "Snake", "Pong", "4 Gewinnt", "Slots", "Tetris"]
                for i, r in enumerate(rects_dict["game_rects"]):
                    if r.collidepoint(pos):
                        self.selected_game = games[i]
                        self.current_key_binding_view = "detail"
                        break

    def handle_key_bindings_detail_events(self, event, rects):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE,
            )
            self.update_fonts()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if rects[0].collidepoint(pos):
                self.current_key_binding_view = "list"
                self.selected_game = None

    def handle_main_menu_events(self, event, option_rects, settings_rect):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE,
            )
            self.update_fonts()
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.state["mouse_hover"] = next(
                (i for i, r in enumerate(option_rects) if r.collidepoint(mouse_pos)),
                -1,
            )
            self.state["settings_hover"] = settings_rect.collidepoint(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Prüfe zuerst den unsichtbaren Secret-Button
            if self.secret_button_rect and self.secret_button_rect.collidepoint(pos):
                self.screen_config["current_view"] = "secret_menu"
            elif self.state["settings_hover"]:
                self.screen_config["current_view"] = "settings"
            elif self.state["mouse_hover"] >= 0:
                if self.state["mouse_hover"] == len(MENU_OPTIONS) - 1:
                    pygame.quit()
                    sys.exit()
                else:
                    self.launch_game(self.state["mouse_hover"])

    def handle_settings_events(self, event, option_rects):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.state["mouse_hover"] = next(
                (i for i, r in enumerate(option_rects) if r.collidepoint(mouse_pos)),
                -1,
            )
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state["mouse_hover"] == 0:
                self.screen_config["settings"]["dark_mode"] = (
                    not self.screen_config["settings"]["dark_mode"]
                )
                self.save_settings()
            elif self.state["mouse_hover"] == 1:
                self.screen_config["current_view"] = "credits"
            elif self.state["mouse_hover"] == 2:
                self.screen_config["current_view"] = "key_bindings"
                self.current_key_binding_view = "list"
                self.selected_game = None
            elif self.state["mouse_hover"] == 3:
                self.screen_config["current_view"] = "main_menu"

    def handle_credits_events(self, event, rects):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE,
            )
            self.update_fonts()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if rects[0].collidepoint(mouse_pos):
                self.screen_config["current_view"] = "settings"

    def launch_game(self, index):
        games = [
            "zweitausendachtundvierzig.py",
            "snake.py",
            "pong.py",
            "viergewint.py",
            "SLOTS.py",
            "Tetris.py",
        ]
        if 0 <= index < len(games):
            game_path = os.path.join(os.path.dirname(__file__), games[index])
            if os.path.exists(game_path):
                subprocess.run([sys.executable, game_path])
                return True
        print(f"Error: Game '{index}' not found!")
        return False

    def run(self):
        while True:
            current_view = self.screen_config["current_view"]
            if current_view == "main_menu":
                option_rects, settings_rect = self.draw_main_menu()
                for event in pygame.event.get():
                    self.handle_main_menu_events(event, option_rects, settings_rect)
            elif current_view == "settings":
                option_rects = self.draw_settings_menu()
                for event in pygame.event.get():
                    self.handle_settings_events(event, option_rects)
            elif current_view == "credits":
                rects = self.draw_credits_menu()
                for event in pygame.event.get():
                    self.handle_credits_events(event, rects)
            elif current_view == "key_bindings":
                if self.current_key_binding_view == "list":
                    rects_dict = self.draw_key_bindings_list()
                    for event in pygame.event.get():
                        self.handle_key_bindings_events(event, rects_dict)
                elif self.current_key_binding_view == "detail":
                    rects = self.draw_key_bindings_detail(self.selected_game)
                    for event in pygame.event.get():
                        self.handle_key_bindings_events(event, rects)
            elif current_view == "secret_menu":
                mines_rect, car_rect, race_rect, back_rect = self.draw_secret_menu()
                for event in pygame.event.get():
                    self.handle_secret_menu_events(event, mines_rect, car_rect, race_rect, back_rect)


if __name__ == "__main__":
    launcher = GameLauncher()  # Instanz des Spiel-Launchers
    launcher.run()              # Starte die Hauptschleife
