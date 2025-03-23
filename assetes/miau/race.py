#!/usr/bin/env python3
import pygame
import math
import sys
import random

pygame.init()
pygame.font.init()

# Bildschirm-Einstellungen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Championship")

# Farben
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (80, 80, 80)
RED        = (255, 0, 0)
BLUE       = (0, 120, 255)
GREEN_MENU = (0, 200, 0)    # Frisches Grün für Menüs
ASPHALT    = (50, 50, 50)   # Asphaltfarbe für den Rennmodus
YELLOW     = (255, 215, 0)
CYAN       = (0, 255, 255)
ORANGE     = (255, 100, 0)

# Spielzustände
STATE_MENU   = "menu"
STATE_GARAGE = "garage"
STATE_RACE   = "race"
current_state = STATE_MENU

# Globale Variablen
player_points = 1000
selected_car_index_player1 = 0

# Streckentypen
TRACK_TYPE_STRAIGHT = 0    # Gerade Strecke mit Wendepunkt (dreispurig)
TRACK_TYPE_OVAL     = 1    # Klassisches Oval
TRACK_TYPE_MIXED    = 2    # Gemischt (Gerade & Kurven)

# Fahrzeugdaten – hier sind mehrere Modelle enthalten
cars = [
    {"name": "Starter",   "power": 150, "mass": 1200, "top_speed": 180, "price": 0,    "owned": True,  "color": RED},
    {"name": "Sports",    "power": 300, "mass": 900,  "top_speed": 280, "price": 500,  "owned": False, "color": BLUE},
    {"name": "Pro Racer", "power": 450, "mass": 700,  "top_speed": 350, "price": 1500, "owned": False, "color": YELLOW},
    {"name": "Turbo",     "power": 350, "mass": 800,  "top_speed": 300, "price": 800,  "owned": False, "color": CYAN},
    {"name": "Lightning", "power": 500, "mass": 650,  "top_speed": 380, "price": 2000, "owned": False, "color": ORANGE}
]

# ----------------------------------------------------------------------------
# Klasse Track: Erzeugt einen Pfad (Liste von Punkten) je nach Streckentyp
# ----------------------------------------------------------------------------
class Track:
    def __init__(self, track_type):
        self.type = track_type
        self.path = []
        self.create_track()

    def create_track(self):
        if self.type == TRACK_TYPE_STRAIGHT:
            # Erzeuge Mittelpfad – bei der Darstellung werden drei Spuren gezeichnet.
            self.path = []
            for x in range(200, 1080, 20):
                self.path.append((x, SCREEN_HEIGHT // 2))
            # Rückfahrt (Wendepunkt)
            for x in range(1080, 200, -20):
                self.path.append((x, (SCREEN_HEIGHT // 2) + 150))
        elif self.type == TRACK_TYPE_OVAL:
            self.path = []
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            for angle in range(0, 360, 5):
                rad = math.radians(angle)
                x = cx + math.cos(rad) * 300
                y = cy + math.sin(rad) * 200
                self.path.append((x, y))
        elif self.type == TRACK_TYPE_MIXED:
            self.path = [(200, 400), (600, 400), (800, 300), (1000, 300),
                         (1200, 500), (800, 500), (600, 600), (200, 600)]

    def draw(self, surface):
        if self.type == TRACK_TYPE_STRAIGHT:
            # Zeichne drei Spuren – Offset in Y-Richtung
            lane_offsets = [-40, 0, 40]
            for offset in lane_offsets:
                lane_points = [(x, y + offset) for (x, y) in self.path]
                pygame.draw.lines(surface, GRAY, False, lane_points, 8)
            # Zeichne Start-/Ziellinie in der mittleren Spur (am ersten Punkt)
            start_point = self.path[0]
            pygame.draw.line(surface, WHITE, (int(start_point[0]), int(start_point[1] - 50)),
                             (int(start_point[0]), int(start_point[1] + 50)), 5)
        else:
            if len(self.path) > 1:
                pygame.draw.lines(surface, GRAY, False, self.path, 8)
                start_point = self.path[0]
                pygame.draw.circle(surface, WHITE, (int(start_point[0]), int(start_point[1])), 10)

# ----------------------------------------------------------------------------
# Klasse Car: Simuliert ein Fahrzeug, das einem vorgegebenen Pfad folgt.
# ----------------------------------------------------------------------------
class Car:
    def __init__(self, car_data, is_player):
        self.name = car_data["name"]
        self.power = car_data["power"]
        self.mass = car_data["mass"]
        self.top_speed = car_data["top_speed"]  # in km/h
        self.color = car_data["color"]
        # Umrechnung: km/h -> Pixel pro Sekunde (1 km/h ≈ 0,27778 m/s – hier vereinfacht als Pixel)
        self.top_speed_pixels = self.top_speed / 3.6
        self.is_player = is_player
        self.speed = 0.0
        self.position = pygame.Vector2(0, 0)  # wird beim Rennstart gesetzt
        self.angle = 0.0
        self.current_checkpoint = 0
        self.lap = 0
        self.crashed = False
        # Nitro-Boost: Nur für den Spieler verfügbar
        if self.is_player:
            self.nitro = 100  # Volle Nitro-Energie (in %)
        else:
            self.nitro = 0
        self.acceleration_rate = (self.power / self.mass) * 80.0
        self.brake_rate = self.acceleration_rate * 1.5

    def update(self, track, dt, accelerate, brake, nitro_active=False):
        if self.crashed:
            self.speed *= 0.95
            return

        # Nitro-Boost: Zusätzliche Beschleunigung, wenn aktiviert und Nitro vorhanden (nur Spieler)
        extra_acceleration = 0
        if self.is_player and nitro_active and self.nitro > 0:
            extra_acceleration = self.acceleration_rate * 0.5
            self.nitro -= 30 * dt  # Nitroverbrauch
            if self.nitro < 0:
                self.nitro = 0
        else:
            # Nitro regenerieren, wenn nicht aktiviert
            if self.is_player and self.nitro < 100:
                self.nitro += 10 * dt
                if self.nitro > 100:
                    self.nitro = 100

        # Geschwindigkeit anpassen
        if accelerate:
            self.speed += (self.acceleration_rate + extra_acceleration) * dt
        elif brake:
            self.speed -= self.brake_rate * dt
        else:
            self.speed *= 0.99

        if self.speed < 0:
            self.speed = 0
        if self.speed > self.top_speed_pixels:
            self.speed = self.top_speed_pixels

        # Berechne den Vektor zum nächsten Checkpoint
        target = pygame.Vector2(track.path[self.current_checkpoint])
        direction = target - self.position
        distance = direction.length()
        if distance > 0:
            direction = direction.normalize()
        else:
            direction = pygame.Vector2(0, 0)

        old_angle = self.angle
        self.angle = math.degrees(math.atan2(direction.y, direction.x))
        move_dist = self.speed * dt
        self.position += direction * move_dist

        # Crash-Mechanismus: In Kurven – wenn die Winkeländerung zu abrupt ist und zu schnell gefahren wird
        if track.type != TRACK_TYPE_STRAIGHT:
            delta_angle = abs((self.angle - old_angle + 180) % 360 - 180)
            if delta_angle > 50 and self.speed > 35:  # Schwellwert: 35 Pixel/s (~126 km/h)
                self.crashed = True

        # Check, ob der aktuelle Checkpoint erreicht wurde
        if distance < 20:
            self.current_checkpoint += 1
            if self.current_checkpoint >= len(track.path):
                self.current_checkpoint = 0
                self.lap += 1

    def draw(self, surface):
        car_width = 40
        car_height = 20
        car_surface = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, car_width, car_height))
        rotated = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated.get_rect(center=(int(self.position.x), int(self.position.y)))
        surface.blit(rotated, rect)
        # Nitro-Anzeige (nur für Spieler)
        if self.is_player:
            nitro_bar_width = 50
            nitro_bar_height = 5
            fill = int((self.nitro / 100) * nitro_bar_width)
            pygame.draw.rect(surface, YELLOW, (int(self.position.x) - 25, int(self.position.y) - 30, fill, nitro_bar_height))
            pygame.draw.rect(surface, WHITE, (int(self.position.x) - 25, int(self.position.y) - 30, nitro_bar_width, nitro_bar_height), 1)
        # Crash-Anzeige
        if self.crashed:
            crash_font = pygame.font.SysFont("Arial", 24)
            crash_text = crash_font.render("CRASH!", True, RED)
            surface.blit(crash_text, (int(self.position.x) - 20, int(self.position.y) - 40))

# ----------------------------------------------------------------------------
# UI-Funktionen
# ----------------------------------------------------------------------------
def race_btn_text(font, text):
    return font.render(text, True, WHITE)

def draw_menu():
    screen.fill(GREEN_MENU)
    title_font = pygame.font.SysFont("Arial", 48)
    title = title_font.render("Racing Championship", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    btn_font = pygame.font.SysFont("Arial", 36)
    race_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 50)
    garage_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 320, 200, 50)
    quit_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 390, 200, 50)
    pygame.draw.rect(screen, GRAY, race_btn)
    pygame.draw.rect(screen, GRAY, garage_btn)
    pygame.draw.rect(screen, GRAY, quit_btn)
    screen.blit(race_btn_text(btn_font, "Race"), (race_btn.x + 45, race_btn.y + 5))
    screen.blit(race_btn_text(btn_font, "Garage"), (garage_btn.x + 25, garage_btn.y + 5))
    screen.blit(race_btn_text(btn_font, "Quit"), (quit_btn.x + 45, quit_btn.y + 5))
    return race_btn, garage_btn, quit_btn

def draw_garage():
    global player_points, selected_car_index_player1
    screen.fill(BLACK)
    title_font = pygame.font.SysFont("Arial", 48)
    title = title_font.render("Garage", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
    info_font = pygame.font.SysFont("Arial", 28)
    points_text = info_font.render(f"Points: {player_points}", True, WHITE)
    screen.blit(points_text, (50, 100))
    car_font = pygame.font.SysFont("Arial", 24)
    margin = 50
    card_width = 250
    card_height = 150
    cards = []
    for i, car in enumerate(cars):
        x = margin + (i % 3) * (card_width + margin)
        y = 200 + (i // 3) * (card_height + margin)
        rect = pygame.Rect(x, y, card_width, card_height)
        pygame.draw.rect(screen, GRAY, rect, 2)
        if i == selected_car_index_player1:
            pygame.draw.rect(screen, YELLOW, rect, 4)
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(screen, car["color"], inner_rect)
        name_text = car_font.render(car["name"], True, WHITE)
        price_text = car_font.render(f"${car['price']}", True, WHITE)
        owned_text = car_font.render("Owned" if car["owned"] else "Buy", True, WHITE)
        screen.blit(name_text, (x + 10, y + 10))
        screen.blit(price_text, (x + 10, y + 40))
        screen.blit(owned_text, (x + 10, y + 70))
        cards.append((rect, i))
    back_btn = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 100, 150, 50)
    pygame.draw.rect(screen, GRAY, back_btn)
    back_text = car_font.render("Back", True, WHITE)
    screen.blit(back_text, (back_btn.x + 30, back_btn.y + 10))
    return cards, back_btn

def draw_race(player_car, ai_car, track):
    # Asphalt-Hintergrund für den Rennmodus
    screen.fill(ASPHALT)
    track.draw(screen)
    player_car.draw(screen)
    ai_car.draw(screen)
    hud_font = pygame.font.SysFont("Arial", 24)
    speed_text = hud_font.render(f"Speed: {int(player_car.speed * 3.6)} km/h", True, WHITE)
    lap_text = hud_font.render(f"Lap: {player_car.lap} / 3", True, WHITE)
    screen.blit(speed_text, (20, 20))
    screen.blit(lap_text, (20, 50))
    quit_btn = pygame.Rect(20, SCREEN_HEIGHT - 80, 150, 50)
    pygame.draw.rect(screen, GRAY, quit_btn)
    quit_text = hud_font.render("Quit Race", True, WHITE)
    screen.blit(quit_text, (quit_btn.x + 10, quit_btn.y + 10))
    
    # Zusatz: Geschwindigkeits-Effekt – wenn hohe Geschwindigkeit, werden dynamische Linien gezeichnet
    if player_car.is_player and player_car.speed > 100:
        effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        num_lines = 10
        # Berechne Intensität basierend auf aktueller Geschwindigkeit
        intensity = min(255, int((player_car.speed - 100) / (player_car.top_speed_pixels - 100) * 255))
        for _ in range(num_lines):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            length = random.randint(20, 100)
            color_with_alpha = (255, 255, 255, intensity)
            pygame.draw.line(effect_surface, color_with_alpha, (x, y), (x, y + length), 2)
        screen.blit(effect_surface, (0, 0))
    
    return quit_btn

def check_race_end(player_car, ai_car):
    if player_car.lap >= 3:
        return "player"
    elif ai_car.lap >= 3:
        return "ai"
    return None

# ----------------------------------------------------------------------------
# Haupt-Spielschleife und Zustandsverwaltung
# ----------------------------------------------------------------------------
def main():
    global current_state, player_points, selected_car_index_player1
    global race_car_player, race_car_ai, current_track

    clock = pygame.time.Clock()
    race_car_player = None
    race_car_ai = None
    current_track = None
    race_result = None
    race_result_timer = 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta-Zeit in Sekunden
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if current_state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    race_btn, garage_btn, quit_btn = draw_menu()
                    if race_btn.collidepoint(mouse_pos):
                        # Starte ein Rennen: Zufällig einen Streckentyp wählen
                        track_type = random.choice([TRACK_TYPE_STRAIGHT, TRACK_TYPE_OVAL, TRACK_TYPE_MIXED])
                        current_track = Track(track_type)
                        # Erstelle Spieler- und KI-Fahrzeuge
                        race_car_player = Car(cars[selected_car_index_player1], True)
                        ai_index = 1 if selected_car_index_player1 == 0 else 0
                        race_car_ai = Car(cars[ai_index], False)
                        start_point = pygame.Vector2(current_track.path[0])
                        race_car_player.position = start_point.copy()
                        race_car_player.current_checkpoint = 0
                        race_car_player.lap = 0
                        race_car_ai.position = start_point.copy() + pygame.Vector2(0, 30)
                        race_car_ai.current_checkpoint = 0
                        race_car_ai.lap = 0
                        race_result = None
                        race_result_timer = 0
                        current_state = STATE_RACE
                    elif garage_btn.collidepoint(mouse_pos):
                        current_state = STATE_GARAGE
                    elif quit_btn.collidepoint(mouse_pos):
                        running = False
                        pygame.quit()
                        sys.exit()
            elif current_state == STATE_GARAGE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    cards, back_btn = draw_garage()
                    for rect, index in cards:
                        if rect.collidepoint(mouse_pos):
                            if not cars[index]["owned"]:
                                if player_points >= cars[index]["price"]:
                                    player_points -= cars[index]["price"]
                                    cars[index]["owned"] = True
                            selected_car_index_player1 = index
                    if back_btn.collidepoint(mouse_pos):
                        current_state = STATE_MENU
            elif current_state == STATE_RACE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    q_btn = draw_race(race_car_player, race_car_ai, current_track)
                    if q_btn.collidepoint(mouse_pos):
                        current_state = STATE_MENU
                        race_result = None
                        race_car_player = None
                        race_car_ai = None
                        current_track = None

        if current_state == STATE_RACE and race_car_player and race_car_ai:
            keys = pygame.key.get_pressed()
            accelerate = keys[pygame.K_UP]
            brake = keys[pygame.K_DOWN]
            nitro_active = keys[pygame.K_SPACE]
            race_car_player.update(current_track, dt, accelerate, brake, nitro_active)
            # KI: immer beschleunigen (ohne Nitro)
            race_car_ai.update(current_track, dt, True, False)
            result = check_race_end(race_car_player, race_car_ai)
            if result:
                race_result = result
                race_result_timer += dt
                if race_result_timer > 2:
                    if race_result == "player":
                        player_points += 500
                    else:
                        player_points = max(0, player_points - 200)
                    current_state = STATE_MENU
                    race_result = None
                    race_result_timer = 0

        if current_state == STATE_MENU:
            draw_menu()
        elif current_state == STATE_GARAGE:
            draw_garage()
        elif current_state == STATE_RACE and race_car_player and race_car_ai:
            draw_race(race_car_player, race_car_ai, current_track)

        pygame.display.flip()

if __name__ == "__main__":
    main()
