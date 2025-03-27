import pygame
import sys
import random
import math
import traceback

try:
    # Initialisiere Pygame
    pygame.init()

    # Basis- und aktuelle Bildschirmdimensionen
    base_width, base_height = 800, 600

    # Vollbild erzwingen
    fullscreen = True
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    width, height = screen.get_size()
    pygame.display.set_caption("Pong")

    # Skalierungsfaktoren berechnen
    scale_x = width / base_width
    scale_y = height / base_height
    scale_factor_x = math.sqrt(scale_x) # Wurzelfaktor für moderatere Größenänderung
    scale_factor_y = math.sqrt(scale_y) # Wurzelfaktor für moderatere Größenänderung

    # Farben
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (200, 200, 200)
    RED = (255, 50, 50)

    # Basis-Spielobjekte
    base_paddle_width, base_paddle_height = 10, 125  # Schläger 25% länger
    base_ball_size = 20

    # Angepasste Dimensionen im Vollbildmodus
    paddle_width = int(base_paddle_width * scale_factor_x)
    paddle_height = int(base_paddle_height * scale_factor_y)
    ball_size = int(base_ball_size * scale_factor_x)
    paddle_speed = int(10 * scale_factor_y) # Geschwindigkeit skaliert mit Höhe
    ai_speed = int(6 * scale_factor_y)      # KI-Geschwindigkeit skaliert mit Höhe
    base_ball_speed = 3.5

    # Initialisierung der Spielobjekte
    paddle1 = pygame.Rect(
        30, height // 2 - paddle_height // 2, paddle_width, paddle_height
    )
    paddle2 = pygame.Rect(
        width - 30 - paddle_width,
        height // 2 - paddle_height // 2,
        paddle_width,
        paddle_height,
    )
    ball = pygame.Rect(
        width // 2 - ball_size // 2, height // 2 - ball_size // 2, ball_size, ball_size
    )

    # Geschwindigkeiten
    ball_speed_x = base_ball_speed
    ball_speed_y = base_ball_speed

    # KI-Eigenschaften
    ai_precision = 0.80  # Auf 80% reduziert
    ai_reaction_delay = 4  # Erhöht (langsamere Reaktion)
    ai_mistake_chance = 0.20  # Auf 20% erhöht
    ai_target_offset = 0  # Zielverschiebung
    ai_frame_counter = 0  # Frame-Zähler

    # KI-Eigenschaften für gezieltes Durchlassen
    ai_hit_counter = 0  # Zählt erfolgreiche Treffer der KI
    ai_hits_until_miss = random.randint(3, 6)  # Zufällige Anzahl, nach der die KI daneben schlägt
    ai_force_miss = False  # Flag zum Erzwingen eines Fehlschlags

    # Punkte
    score1, score2 = 0, 0

    # Fonts
    font = pygame.font.Font(None, int(74 * scale_factor_y)) # Skalierte Schriftgröße
    small_font = pygame.font.Font(None, int(36 * scale_factor_y)) # Skalierte Schriftgröße

    # Spielzustände
    STATE_MENU = 0
    STATE_MODE_SELECT = 1
    STATE_GAME = 2
    STATE_GAME_OVER = 3
    current_state = STATE_MENU

    # Spielmodus-Flags
    is_singleplayer = True
    is_hardcore = False

    # Clock für FPS-Begrenzung
    clock = pygame.time.Clock()

    # Button-Rects für aktive Buttons
    button_rects = {}

    def reset_game():
        """Setzt das Spiel zurück"""
        global paddle1, paddle2, ball, score1, score2, ball_speed_x, ball_speed_y, \
            ai_hit_counter, ai_force_miss, ai_hits_until_miss

        # Schläger mit aktueller Größe erstellen
        paddle1 = pygame.Rect(
            30, height // 2 - paddle_height // 2, paddle_width, paddle_height
        )
        paddle2 = pygame.Rect(
            width - 30 - paddle_width,
            height // 2 - paddle_height // 2,
            paddle_width,
            paddle_height,
        )

        # Ball mit aktueller Größe erstellen
        ball = pygame.Rect(
            width // 2 - ball_size // 2, height // 2 - ball_size // 2, ball_size, ball_size
        )

        score1, score2 = 0, 0

        # Geschwindigkeit basierend auf aktueller Bildschirmgröße berechnen
        speed_factor_x = width / base_width
        speed_factor_y = height / base_height

        # Wurzelfaktor für moderatere Geschwindigkeit im Vollbildmodus
        if fullscreen:
            speed_factor_x = math.sqrt(speed_factor_x)
            speed_factor_y = math.sqrt(speed_factor_y)

        ball_speed_x = base_ball_speed * speed_factor_x * random.choice([-1, 1])
        ball_speed_y = base_ball_speed * speed_factor_y * random.choice([-1, 1])

        # KI-Zähler zurücksetzen
        ai_hit_counter = 0
        ai_force_miss = False
        ai_hits_until_miss = random.randint(3, 6)

    def select_singleplayer():
        """Wählt den Einzelspielermodus und geht zur Modusauswahl"""
        global current_state, is_singleplayer
        is_singleplayer = True
        current_state = STATE_MODE_SELECT

    def select_multiplayer():
        """Wählt den Mehrspielermodus und geht zur Modusauswahl"""
        global current_state, is_singleplayer
        is_singleplayer = False
        current_state = STATE_MODE_SELECT

    def start_normal_mode():
        """Startet den normalen Spielmodus"""
        global current_state, is_hardcore
        is_hardcore = False
        reset_game()
        current_state = STATE_GAME

    def start_hardcore_mode():
        """Startet den Hardcore-Spielmodus"""
        global current_state, is_hardcore
        is_hardcore = True
        reset_game()
        current_state = STATE_GAME

    def quit_game():
        """Beendet das Spiel"""
        pygame.quit()
        sys.exit()

    def return_to_menu():
        """Kehrt zum Hauptmenü zurück"""
        global current_state
        current_state = STATE_MENU

    def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
        """Zeichnet einen Button und speichert seine Informationen für spätere Klickverarbeitung"""
        global button_rects

        # Skalierte Button-Dimensionen und Positionen
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_w = int(w * scale_x)
        scaled_h = int(h * scale_y)

        button_rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)
        button_rects[text] = (button_rect, action) # Speichere das skalierte Rect

        # Mausposition sicher abrufen
        try:
            mouse = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse)
        except Exception:
            hover = False

        pygame.draw.rect(screen, active_color if hover else inactive_color, button_rect)
        text_surface = small_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center) # Zentriert im skalierten Button
        screen.blit(text_surface, text_rect)

    def handle_button_click(pos):
        """Behandelt Buttonklicks an der angegebenen Position"""
        for _, (rect, action) in button_rects.items():
            if rect.collidepoint(pos) and action:
                action()
                return True
        return False

    def handle_events():
        """Behandelt globale Events wie Beenden und Mausklicks"""
        global current_state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state in (STATE_GAME, STATE_MODE_SELECT, STATE_GAME_OVER):
                        current_state = STATE_MENU
                    elif current_state == STATE_MENU:
                        quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    handle_button_click(event.pos)

    def menu():
        """Zeigt das Hauptmenü an"""
        global button_rects

        button_rects = {}
        screen.fill(BLACK)

        # Titel (skaliert)
        title = font.render("PONG", True, WHITE)
        title_rect = title.get_rect(center=(width // 2, int(100 * scale_y)))
        screen.blit(title, title_rect)

        # Buttons (Basis-Positionen, werden in draw_button skaliert)
        button_width, button_height = 300, 50
        button_x = base_width // 2 - button_width // 2 # Basis-X

        draw_button("Einzelspieler", button_x, 250, button_width, button_height,
                    GRAY, LIGHT_GRAY, select_singleplayer)
        draw_button("Mehrspieler", button_x, 320, button_width, button_height,
                    GRAY, LIGHT_GRAY, select_multiplayer)
        draw_button("Beenden", button_x, 390, button_width, button_height,
                    GRAY, LIGHT_GRAY, quit_game)

        pygame.display.flip()

    def mode_select():
        """Zeigt die Schwierigkeitsauswahl"""
        global button_rects
        button_rects = {}
        screen.fill(BLACK)

        # Titel (skaliert)
        title = font.render("Spielmodus wählen", True, WHITE)
        title_rect = title.get_rect(center=(width // 2, int(100 * scale_y)))
        screen.blit(title, title_rect)

        # Modus-Text (skaliert)
        mode_text_content = "Einzelspieler" if is_singleplayer else "Mehrspieler"
        mode_text = small_font.render(mode_text_content, True, WHITE)
        mode_text_rect = mode_text.get_rect(center=(width // 2, int(180 * scale_y)))
        screen.blit(mode_text, mode_text_rect)

        # Buttons (Basis-Positionen)
        button_width, button_height = 300, 50
        button_x = base_width // 2 - button_width // 2 # Basis-X

        draw_button("Normal", button_x, 250, button_width, button_height,
                    GRAY, LIGHT_GRAY, start_normal_mode)
        draw_button("Hardcore", button_x, 320, button_width, button_height,
                    GRAY, RED, start_hardcore_mode)
        draw_button("Zurück", button_x, 390, button_width, button_height,
                    GRAY, LIGHT_GRAY, return_to_menu)

        pygame.display.flip()

    def game_over():
        """Zeigt den Game-Over-Bildschirm an"""
        global button_rects

        button_rects = {}
        screen.fill(BLACK)

        if score1 >= 10:
            winner_text = "Spieler 1 gewinnt!"
        else:
            winner_text = "Spieler 2 gewinnt!"

        # Text (skaliert)
        winner_surface = font.render(
            winner_text, True, RED if is_hardcore else WHITE
        )
        winner_rect = winner_surface.get_rect(center=(width // 2, height // 2 - int(50 * scale_y)))
        screen.blit(winner_surface, winner_rect)

        score_surface = font.render(
            f"{score1} - {score2}", True, RED if is_hardcore else WHITE
        )
        score_rect = score_surface.get_rect(center=(width // 2, height // 2 + int(30 * scale_y)))
        screen.blit(score_surface, score_rect)

        # Button (Basis-Positionen)
        draw_button("Zurück zum Menü", base_width // 2 - 150, base_height // 2 + 120, 300,
                    50, GRAY, LIGHT_GRAY, return_to_menu)

        pygame.display.flip()

    def game_loop():
        """Hauptspielschleife"""
        global score1, score2, ball_speed_x, ball_speed_y, current_state, \
            ai_frame_counter, ai_target_offset, ai_hit_counter, ai_hits_until_miss, \
            ai_force_miss

        keys = pygame.key.get_pressed()

        # --- Spieler 1 (linker Schläger) ---
        # Steuerung mit W/S ODER Pfeiltasten (Hoch/Runter)
        move_up = keys[pygame.K_w] or keys[pygame.K_UP]
        move_down = keys[pygame.K_s] or keys[pygame.K_DOWN]

        if move_up and paddle1.top > 0:
            paddle1.y -= paddle_speed
        # Benutze elif hier, falls jemand W und S (oder Hoch und Runter) gleichzeitig drückt
        elif move_down and paddle1.bottom < height:
            paddle1.y += paddle_speed


        # --- Spieler 2 (rechter Schläger) ---
        # Steuerung durch KI im Einzelspieler oder Pfeiltasten im Mehrspieler
        if is_singleplayer:
            # --- KI-Logik (UNVERÄNDERT) ---
            if ball_speed_x > 0:  # Ball bewegt sich zum rechten Schläger
                ai_frame_counter += 1

                if ai_force_miss:
                    # KI zielt absichtlich daneben
                    target_y = ball.centery + 200 * scale_y * ( # Skalierter Offset
                        1 if ball.centery < height / 2 else -1
                    )
                else:
                    # Normale KI-Zielberechnung mit Fehlern
                    if random.random() < ai_mistake_chance and ai_frame_counter % 60 == 0:
                        ai_target_offset = random.randint(int(-50 * scale_y), int(50 * scale_y)) # Skalierter Offset

                    target_y = ball.centery + ai_target_offset

                    if random.random() > ai_precision:
                        target_y += random.randint(int(-30 * scale_y), int(30 * scale_y)) # Skalierter Offset

                # KI bewegt den Schläger zum Ziel
                if paddle2.centery < target_y and paddle2.bottom < height:
                    paddle2.y += ai_speed
                elif paddle2.centery > target_y and paddle2.top > 0:
                    paddle2.y -= ai_speed

                # Reaktionsverzögerung
                if ai_frame_counter > ai_reaction_delay:
                    ai_frame_counter = 0
            # --- Ende KI-Logik ---

        else: # Mehrspieler-Modus
            # Im Mehrspieler steuern die Pfeiltasten Spieler 2
            # (Wichtig: Diese Logik wird jetzt nur noch im Mehrspieler-Modus relevant,
            # da die Pfeiltasten für Spieler 1 oben abgefragt werden)
            if keys[pygame.K_UP] and paddle2.top > 0:
                paddle2.y -= paddle_speed
            if keys[pygame.K_DOWN] and paddle2.bottom < height:
                paddle2.y += paddle_speed

        # --- Ballbewegung und Kollision ---
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball-Kollision mit oberem/unterem Rand
        if ball.top <= 0 or ball.bottom >= height:
            ball_speed_y *= -1
            # Sicherstellen, dass der Ball nicht im Rand stecken bleibt
            if ball.top < 0: ball.top = 0
            if ball.bottom > height: ball.bottom = height


        # Ball-Kollision mit Schlägern
        collision_occurred = False
        if ball.colliderect(paddle1) and ball_speed_x < 0: # Nur bei Bewegung nach links
            ball_speed_x *= -1
            collision_occurred = True
            # Ball leicht aus dem Schläger schieben, um Mehrfachkollisionen zu vermeiden
            ball.left = paddle1.right
            # KI-Zähler zurücksetzen, falls der Spieler trifft
            ai_hit_counter = 0
            ai_force_miss = False
            ai_hits_until_miss = random.randint(3, 6)

        if ball.colliderect(paddle2) and ball_speed_x > 0: # Nur bei Bewegung nach rechts
            ball_speed_x *= -1
            collision_occurred = True
            # Ball leicht aus dem Schläger schieben
            ball.right = paddle2.left
            # KI-Treffer nur zählen, wenn die KI auch aktiv ist
            if is_singleplayer:
                ai_hit_counter += 1
                if ai_hit_counter >= ai_hits_until_miss:
                    ai_force_miss = True # Nächster Treffer wird ein Fehlschlag

        # Geschwindigkeitsanpassung nach Kollision
        if collision_occurred:
            if is_hardcore:
                ball_speed_x *= 1.10
                ball_speed_y *= 1.10

            # Leichte zufällige Änderung des Y-Winkels
            # Skalierter Y-Speed-Change
            y_change = random.uniform(-1 * scale_factor_y, 1 * scale_factor_y)
            ball_speed_y += y_change

            # Begrenzung der Y-Geschwindigkeit (skaliert)
            max_y_speed = 8 * scale_factor_y
            ball_speed_y = max(-max_y_speed, min(max_y_speed, ball_speed_y))
            # Begrenzung der X-Geschwindigkeit (skaliert)
            max_x_speed = 15 * scale_factor_x
            ball_speed_x = max(-max_x_speed, min(max_x_speed, ball_speed_x))


        # --- Punktevergabe und Ball-Reset ---
        point_scored = False
        # Ball außerhalb des Spielfelds - linker Rand (Spieler 1 verfehlt)
        if ball.left <= 0:
            score2 += 1
            point_scored = True

        # Ball außerhalb des Spielfelds - rechter Rand (Spieler 2 / KI verfehlt)
        if ball.right >= width:
            score1 += 1
            point_scored = True

        if point_scored:
            # Ball zurücksetzen
            ball.center = (width // 2, height // 2)
            # Geschwindigkeit zurücksetzen und Richtung ändern
            speed_factor_x = math.sqrt(scale_x) if fullscreen else scale_x
            speed_factor_y = math.sqrt(scale_y) if fullscreen else scale_y
            # Richtung zum Verlierer des Punktes
            direction_x = 1 if ball.left <= 0 else -1 # Wenn links raus -> Start nach rechts (zu P2)
            ball_speed_x = base_ball_speed * speed_factor_x * direction_x
            ball_speed_y = base_ball_speed * speed_factor_y * random.choice([-1, 1])
            # KI-Fehler-Zähler zurücksetzen
            ai_hit_counter = 0
            ai_force_miss = False
            ai_hits_until_miss = random.randint(3, 6)
            # Kurze Pause nach Punkt (optional)
            # pygame.time.wait(500)


        # --- Zeichnen ---
        screen.fill(BLACK)
        color = RED if is_hardcore else WHITE
        pygame.draw.aaline(screen, color, (width // 2, 0), (width // 2, height))
        pygame.draw.rect(screen, color, paddle1)
        pygame.draw.rect(screen, color, paddle2)
        pygame.draw.ellipse(screen, color, ball)

        # Punktestand (skaliert)
        score_text = font.render(f"{score1} - {score2}", True, color)
        score_rect = score_text.get_rect(center=(width // 2, int(30 * scale_y)))
        screen.blit(score_text, score_rect)

        # Modus-Anzeige (skaliert)
        mode_string = "Einzelspieler" if is_singleplayer else "Mehrspieler"
        if is_hardcore:
            mode_string += " - Hardcore"
        mode_text = small_font.render(mode_string, True, color)
        mode_rect = mode_text.get_rect(topright=(width - int(10 * scale_x), int(10 * scale_y)))
        screen.blit(mode_text, mode_rect)

        # ESC-Hinweis (skaliert)
        esc_text = small_font.render("ESC = Menü", True, color)
        esc_rect = esc_text.get_rect(topleft=(int(10 * scale_x), int(10 * scale_y)))
        screen.blit(esc_text, esc_rect)

        # Spielende prüfen
        if score1 >= 10 or score2 >= 10:
            current_state = STATE_GAME_OVER

        pygame.display.flip()

    # Hauptschleife
    running = True
    while running:
        handle_events() # Events zuerst behandeln

        # Zustandslogik
        if current_state == STATE_MENU:
            menu()
        elif current_state == STATE_MODE_SELECT:
            mode_select()
        elif current_state == STATE_GAME:
            game_loop()
        elif current_state == STATE_GAME_OVER:
            game_over()

        clock.tick(144) # FPS-Limit (z.B. 144)

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    traceback.print_exc()
finally: # Sicherstellen, dass Pygame beendet wird
    pygame.quit()
    sys.exit()

