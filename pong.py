import pygame
import sys

# Initialisiere Pygame
pygame.init()

# Standard Bildschirmdimensionen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddles and ball
paddle_width, paddle_height = 10, 100
ball_size = 20
paddle1 = pygame.Rect(30, height // 2 - paddle_height // 2, paddle_width, paddle_height)
paddle2 = pygame.Rect(width - 30 - paddle_width, height // 2 - paddle_height // 2, paddle_width, paddle_height)
ball = pygame.Rect(width // 2 - ball_size // 2, height // 2 - ball_size // 2, ball_size, ball_size)

# Speeds
paddle_speed = 10
ball_speed_x, ball_speed_y = 5, 5

# Scores
score1, score2 = 0, 0
font = pygame.font.Font(None, 74)

# Clock
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1.top > 0:
        paddle1.y -= paddle_speed
    if keys[pygame.K_s] and paddle1.bottom < height:
        paddle1.y += paddle_speed
    if keys[pygame.K_UP] and paddle2.top > 0:
        paddle2.y -= paddle_speed
    if keys[pygame.K_DOWN] and paddle2.bottom < height:
        paddle2.y += paddle_speed

    # Move ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with top/bottom
    if ball.top <= 0 or ball.bottom >= height:
        ball_speed_y *= -1

    # Ball collision with paddles
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_speed_x *= -1

    # Ball out of bounds
    if ball.left <= 0:
        score2 += 1
        ball.x, ball.y = width // 2 - ball_size // 2, height // 2 - ball_size // 2
    if ball.right >= width:
        score1 += 1
        ball.x, ball.y = width // 2 - ball_size // 2, height // 2 - ball_size // 2

    # Fill screen
    screen.fill(BLACK)

    # Draw paddles and ball
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Display score
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 20))

    # Check for game over
    if score1 >= 10 or score2 >= 10:
        winner_text = "Spiel Beendet! "
        if score1 >= 10:
            winner_text += "Spieler 1 gewinnt!"
        else:
            winner_text += "Spieler 2 gewinnt!"
        winner_surface = font.render(winner_text, True, WHITE)
        screen.blit(winner_surface, (width // 2 - winner_surface.get_width() // 2, height // 2 - winner_surface.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    # Update display
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()