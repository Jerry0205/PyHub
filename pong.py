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
    scale_factor_x = math.sqrt(scale_x)
    scale_factor_y = math.sqrt(scale_y)

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
    paddle_speed = int(10 * scale_factor_y)
    ai_speed = int(6 * scale_factor_y)
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
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

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

        button_rect = pygame.Rect(x, y, w, h)
        button_rects[text] = (button_rect, action)

        # Mausposition sicher abrufen
        try:
            mouse = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse)
        except Exception:
            hover = False

        pygame.draw.rect(screen, active_color if hover else inactive_color, button_rect)
        text_surface = small_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
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
                    if current_state in (STATE_GAME, STATE_MODE_SELECT):
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

        # Titel
        title = font.render("PONG", True, WHITE)
        screen.blit(title, (width // 2 - title.get_width() // 2, 100))

        # Buttons (der "Vollbild"-Button wurde entfernt)
        button_width, button_height = 300, 50
        button_x = width // 2 - button_width // 2

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

        title = font.render("Spielmodus wählen", True, WHITE)
        screen.blit(title, (width // 2 - title.get_width() // 2, 100))

        mode_text = small_font.render(
            "Einzelspieler" if is_singleplayer else "Mehrspieler", True, WHITE
        )
        screen.blit(mode_text, (width // 2 - mode_text.get_width() // 2, 180))

        button_width, button_height = 300, 50
        button_x = width // 2 - button_width // 2

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

        winner_surface = font.render(
            winner_text, True, RED if is_hardcore else WHITE
        )
        screen.blit(
            winner_surface,
            (width // 2 - winner_surface.get_width() // 2, height // 2 - 50),
        )

        score_surface = font.render(
            f"{score1} - {score2}", True, RED if is_hardcore else WHITE
        )
        screen.blit(
            score_surface,
            (width // 2 - score_surface.get_width() // 2, height // 2 + 30),
        )

        draw_button("Zurück zum Menü", width // 2 - 150, height // 2 + 120, 300,
                    50, GRAY, LIGHT_GRAY, return_to_menu)

        pygame.display.flip()

    def game_loop():
        """Hauptspielschleife"""
        global score1, score2, ball_speed_x, ball_speed_y, current_state, \
            ai_frame_counter, ai_target_offset, ai_hit_counter, ai_hits_until_miss, \
            ai_force_miss

        keys = pygame.key.get_pressed()

        # Spieler 1 (linker Schläger) - W/S
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= paddle_speed
        if keys[pygame.K_s] and paddle1.bottom < height:
            paddle1.y += paddle_speed

        # Spieler 2 (rechter Schläger) - KI oder Pfeiltasten
        if is_singleplayer:
            if ball_speed_x > 0:  # Ball bewegt sich zum rechten Schläger
                ai_frame_counter += 1

                if ai_force_miss:
                    target_y = ball.centery + 200 * (
                        1 if ball.centery < height / 2 else -1
                    )
                else:
                    if random.random() < ai_mistake_chance and ai_frame_counter % 60 == 0:
                        ai_target_offset = random.randint(-50, 50)

                    target_y = ball.centery + ai_target_offset

                    if random.random() > ai_precision:
                        target_y += random.randint(-30, 30)

                if paddle2.centery < target_y and paddle2.bottom < height:
                    paddle2.y += ai_speed
                elif paddle2.centery > target_y and paddle2.top > 0:
                    paddle2.y -= ai_speed

                if ai_frame_counter > ai_reaction_delay:
                    ai_frame_counter = 0
        else:
            if keys[pygame.K_UP] and paddle2.top > 0:
                paddle2.y -= paddle_speed
            if keys[pygame.K_DOWN] and paddle2.bottom < height:
                paddle2.y += paddle_speed

        # Ball bewegen
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball-Kollision mit oberem/unterem Rand
        if ball.top <= 0 or ball.bottom >= height:
            ball_speed_y *= -1

        # Ball-Kollision mit Schlägern
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            if ball.colliderect(paddle2) and ball_speed_x > 0:
                ai_hit_counter += 1
                if ai_hit_counter >= ai_hits_until_miss:
                    ai_force_miss = True
                    ai_hit_counter = 0
                    ai_hits_until_miss = random.randint(3, 6)

            ball_speed_x *= -1

            if is_hardcore:
                ball_speed_x *= 1.10
                ball_speed_y *= 1.10

            ball_speed_y += random.uniform(-1, 1)
            if abs(ball_speed_y) > 8:
                ball_speed_y = 8 * (1 if ball_speed_y > 0 else -1)

        # Ball außerhalb des Spielfelds - linker Rand
        if ball.left <= 0:
            score2 += 1
            ball.x = width // 2 - ball_size // 2
            ball.y = height // 2 - ball_size // 2

            speed_factor_x = width / base_width
            speed_factor_y = height / base_height

            if fullscreen:
                speed_factor_x = math.sqrt(speed_factor_x)
                speed_factor_y = math.sqrt(speed_factor_y)

            ball_speed_x = base_ball_speed * speed_factor_x
            ball_speed_y = base_ball_speed * speed_factor_y * random.choice([-1, 1])

            ai_hit_counter = 0
            ai_force_miss = False

        # Ball außerhalb des Spielfelds - rechter Rand
        if ball.right >= width:
            score1 += 1
            ball.x = width // 2 - ball_size // 2
            ball.y = height // 2 - ball_size // 2

            speed_factor_x = width / base_width
            speed_factor_y = height / base_height

            if fullscreen:
                speed_factor_x = math.sqrt(speed_factor_x)
                speed_factor_y = math.sqrt(speed_factor_y)

            ball_speed_x = -base_ball_speed * speed_factor_x
            ball_speed_y = base_ball_speed * speed_factor_y * random.choice([-1, 1])

            ai_hit_counter = 0
            ai_force_miss = False

        screen.fill(BLACK)
        color = RED if is_hardcore else WHITE
        pygame.draw.aaline(screen, color, (width // 2, 0), (width // 2, height))
        pygame.draw.rect(screen, color, paddle1)
        pygame.draw.rect(screen, color, paddle2)
        pygame.draw.ellipse(screen, color, ball)

        score_text = font.render(f"{score1} - {score2}", True, color)
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 20))

        mode_text = small_font.render(
            f"{'Einzelspieler' if is_singleplayer else 'Mehrspieler'}{' - Hardcore' if is_hardcore else ''}",
            True,
            color,
        )
        screen.blit(mode_text, (width - mode_text.get_width() - 10, 10))

        esc_text = small_font.render("ESC = Menü", True, color)
        screen.blit(esc_text, (10, 10))

        if score1 >= 10 or score2 >= 10:
            current_state = STATE_GAME_OVER

        pygame.display.flip()

    # Hauptschleife
    running = True
    while running:
        handle_events()

        if current_state == STATE_MENU:
            menu()
        elif current_state == STATE_MODE_SELECT:
            mode_select()
        elif current_state == STATE_GAME:
            game_loop()
        elif current_state == STATE_GAME_OVER:
            game_over()

        clock.tick(244)

except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    traceback.print_exc()
    pygame.quit()
    sys.exit()
