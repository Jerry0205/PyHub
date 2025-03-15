# Hauptimporte
import pygame
import subprocess
import os
import json
import sys

# Konfigurationskonstanten
CONFIG_FILE = "config.json"  # Datei für gespeicherte Einstellungen
HIGHLIGHT_COLOR = (0, 122, 255, 128)  # Farbe für Hervorhebungen
MENU_OPTIONS = [
    "2048",
    "Snake",
    "Pong",
    "4 Gewinnt",
    "Slots",
    "Beenden",
]  # Letzte Option beendet das Programm
SETTINGS_OPTIONS = ["Dark Mode", "Back"]  # Einstellungsoptionen


class GameLauncher:
    def __init__(self):
        # Initialisiert den Spielstarter mit Standardwerten
        self.screen_config = {
            "width": 0,                   # Aktuelle Bildschirmbreite
            "height": 0,                  # Aktuelle Bildschirmhöhe
            "surface": None,              # Pygame-Bildschirmoberfläche
            "fonts": {},                  # Geladene Schriftarten
            "current_view": "main_menu",  # Aktive Ansicht (Hauptmenü/Einstellungen)
            "settings": {"dark_mode": False},
        }

        # Zustandsvariablen, basierend auf Mausinteraktionen
        self.state = {
            "mouse_hover": -1,      # Überfahrener Menüpunkt (Maus)
            "settings_hover": False  # Über Settings-Button schweben (Maus)
        }

        self.init_pygame()    # Pygame initialisieren
        self.load_settings()  # Einstellungen laden
        self.update_fonts()   # Schriftarten erstellen
        self.load_assets()    # Assets (z. B. Logo) laden

    def init_pygame(self):
        # Initialisiert Pygame und den Bildschirm
        pygame.init()
        info = pygame.display.Info()
        self.screen_config["width"] = info.current_w
        self.screen_config["height"] = info.current_h
        self.screen_config["surface"] = pygame.display.set_mode(
            (self.screen_config["width"], self.screen_config["height"]),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("PYHUB")

    def load_settings(self):
        # Lädt Einstellungen aus JSON-Datei
        try:
            with open(CONFIG_FILE, "r") as file:
                self.screen_config["settings"] = json.load(file)
        except FileNotFoundError:
            self.save_settings()  # Erstellt Datei, falls nicht vorhanden

    def save_settings(self):
        # Speichert Einstellungen in JSON-Datei
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.screen_config["settings"], file)

    def update_fonts(self):
        # Aktualisiert Schriftarten bei Größenänderung
        h = self.screen_config["height"]
        self.screen_config["fonts"] = {
            "title": pygame.font.Font(None, h // 10),   # Titelschrift
            "option": pygame.font.Font(None, h // 15),    # Menüschrift
            "button": pygame.font.Font(None, h // 20),    # Buttonschrift
        }

    def load_assets(self):
        # Lädt Assets, z. B. die Logos aus dem Ordner "assetes"
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Lade beide Logos
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
        # Gibt aktuelle Farben basierend auf Dark Mode zurück
        dark = self.screen_config["settings"]["dark_mode"]
        return (
            (0, 0, 0) if dark else (255, 255, 255),  # Hintergrundfarbe
            (255, 255, 255) if dark else (0, 0, 0)     # Textfarbe
        )

    def draw_highlight(self, rect):
        # Zeichnet Hintergrund-Highlight für ausgewählte Elemente
        highlight = pygame.Surface(
            (rect.width + 30, rect.height + 20), pygame.SRCALPHA
        )
        pygame.draw.rect(
            highlight, HIGHLIGHT_COLOR, highlight.get_rect(), border_radius=5
        )
        self.screen_config["surface"].blit(highlight, (rect.x - 15, rect.y - 10))

    def draw_main_menu(self):
        # Zeichnet das Hauptmenü mit allen Elementen
        bg_color, text_color = self.get_colors()
        screen = self.screen_config["surface"]
        screen.fill(bg_color)

        # Überschrift: Logo einfügen (falls vorhanden)
        # Wähle das Logo basierend auf dem Dark Mode-Status
        current_logo = self.dark_logo if self.screen_config["settings"]["dark_mode"] else self.white_logo
        
        if current_logo is not None:
            # Skalieren des Logos relativ zur Fenstergröße - HIER WURDE DIE GRÖSSE ANGEPASST
            logo_width = self.screen_config["width"] // 4  # Größer (war vorher // 4)
            logo_height = self.screen_config["height"] // 2.5
              # Größer (war vorher // 8)
            logo_scaled = pygame.transform.scale(
                current_logo, (logo_width, logo_height)
            )
            logo_rect = logo_scaled.get_rect(
                center=(self.screen_config["width"] // 2,
                        self.screen_config["height"] // 7)  # Höher positioniert
            )
            screen.blit(logo_scaled, logo_rect)
        else:
            # Fallback: Text, falls kein Logo vorhanden ist
            title = self.screen_config["fonts"]["title"].render(
                "PYHUB", True, text_color
            )
            title_rect = title.get_rect(
                center=(self.screen_config["width"] // 2,
                        self.screen_config["height"] // 8)
            )
            screen.blit(title, title_rect)

        # Settings-Button (separat gezeichnet)
        button_text = "Settings"
        button_font = self.screen_config["fonts"]["button"]
        button_surf = button_font.render(button_text, True, text_color)
        button_rect = button_surf.get_rect(
            midleft=(
                self.screen_config["width"] // 2 + self.screen_config["width"] // 8,
                self.screen_config["height"] // 7  # Angepasst an die neue Logo-Position
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
                    i * (self.screen_config["height"] // 12)
                )
            )
            if i == self.state["mouse_hover"]:
                self.draw_highlight(option_rect)
            screen.blit(option_surf, option_rect)
            option_rects.append(option_rect)

        pygame.display.flip()
        return option_rects, button_rect

    def draw_settings_menu(self):
        # Zeichnet das Einstellungsmenü
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

        # Einstellungsoptionen zeichnen
        option_rects = []
        for i, option in enumerate(SETTINGS_OPTIONS):
            font = self.screen_config["fonts"]["option"]
            option_surf = font.render(option, True, text_color)
            option_rect = option_surf.get_rect(
                center=(
                    self.screen_config["width"] // 2,
                    self.screen_config["height"] // 4 +
                    i * (self.screen_config["height"] // 12)
                )
            )
            if i == self.state["mouse_hover"]:
                self.draw_highlight(option_rect)
            screen.blit(option_surf, option_rect)
            option_rects.append(option_rect)

        pygame.display.flip()
        return option_rects

    def handle_main_menu_events(self, event, option_rects, settings_rect):
        # Verarbeitet Ereignisse im Hauptmenü (nur Maus-Eingaben)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            # Anpassung bei Fenstergrößenänderung
            self.screen_config["width"], self.screen_config["height"] = event.w, event.h
            self.screen_config["surface"] = pygame.display.set_mode(
                (self.screen_config["width"], self.screen_config["height"]),
                pygame.RESIZABLE
            )
            self.update_fonts()

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.state["mouse_hover"] = next(
                (i for i, r in enumerate(option_rects) if r.collidepoint(mouse_pos)),
                -1
            )
            self.state["settings_hover"] = settings_rect.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state["settings_hover"]:
                self.screen_config["current_view"] = "settings"
            elif self.state["mouse_hover"] >= 0:
                # Bei Klick auf "Beenden" (letzte Option) wird das Programm beendet
                if self.state["mouse_hover"] == len(MENU_OPTIONS) - 1:
                    pygame.quit()
                    sys.exit()
                else:
                    self.launch_game(self.state["mouse_hover"])

    def handle_settings_events(self, event, option_rects):
        # Verarbeitet Ereignisse im Einstellungsmenü (nur Maus-Eingaben)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.state["mouse_hover"] = next(
                (i for i, r in enumerate(option_rects) if r.collidepoint(mouse_pos)),
                -1
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state["mouse_hover"] == 0:
                # Dark Mode umschalten
                self.screen_config["settings"]["dark_mode"] = not (
                    self.screen_config["settings"]["dark_mode"]
                )
                self.save_settings()
            elif self.state["mouse_hover"] == 1:
                self.screen_config["current_view"] = "main_menu"

    def launch_game(self, index):
        # Startet das ausgewählte Spiel
        games = [
            "zweitausendachtundvierzig.py",
            "snake.py",
            "pong.py",
            "viergewint.py",
            "SLOTS.py"
        ]

        if 0 <= index < len(games):
            game_path = os.path.join(os.path.dirname(__file__), games[index])
            if os.path.exists(game_path):
                subprocess.run([sys.executable, game_path])
                return True

        print(f"Error: Game '{index}' not found!")
        return False

    def run(self):
        # Hauptschleife des Programms
        while True:
            if self.screen_config["current_view"] == "main_menu":
                option_rects, settings_rect = self.draw_main_menu()
                for event in pygame.event.get():
                    self.handle_main_menu_events(event, option_rects, settings_rect)
            elif self.screen_config["current_view"] == "settings":
                option_rects = self.draw_settings_menu()
                for event in pygame.event.get():
                    self.handle_settings_events(event, option_rects)


if __name__ == "__main__":
    launcher = GameLauncher()  # Erstellt Instanz des Spiel-Launchers
    launcher.run()  # Startet die Hauptschleife
