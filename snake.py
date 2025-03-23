from tkinter import *
import random

# Konstanten
SPEED = 150
SPACE_SIZE = 50
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"      # grün
FOOD_COLOR = "#FF0000"       # rot
BACKGROUND_COLOR = "#000000" # schwarz

# Globale Variablen
score = 0
direction = "down"
snake = None
food = None
start_button = None
restart_button = None
score_label = None

# --- Klassen ---

class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        # Startposition: Alle Segmente starten bei (0,0)
        for _ in range(BODY_PARTS):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = canvas.create_rectangle(
                x,
                y,
                x + SPACE_SIZE,
                y + SPACE_SIZE,
                fill=SNAKE_COLOR,
                tag="snake",
                outline="",
            )
            self.squares.append(square)


class Food:
    def __init__(self):
        # Zufällige Platzierung, angepasst an die Canvas-Größe
        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        self.coordinates = [x, y]
        canvas.create_oval(
            x,
            y,
            x + SPACE_SIZE,
            y + SPACE_SIZE,
            fill=FOOD_COLOR,
            tag="food",
            outline="",
        )


# --- Funktionen der Spielmechanik ---

def next_turn(snake, food):
    global direction, score, score_label

    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    # Neuen Kopf einfügen
    snake.coordinates.insert(0, [x, y])
    square = canvas.create_rectangle(
        x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake", outline=""
    )
    snake.squares.insert(0, square)

    if x == food.coordinates[0] and y == food.coordinates[1]:
        score += 1
        score_label.config(text="Score: {}".format(score))
        canvas.delete("food")
        food = Food()
    else:
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    if check_collisions(snake):
        game_over()
    else:
        window.after(SPEED, next_turn, snake, food)


def change_direction(new_direction):
    global direction
    if new_direction == "left" and direction != "right":
        direction = new_direction
    elif new_direction == "right" and direction != "left":
        direction = new_direction
    elif new_direction == "up" and direction != "down":
        direction = new_direction
    elif new_direction == "down" and direction != "up":
        direction = new_direction


def check_collisions(snake):
    x, y = snake.coordinates[0]

    # Kollision mit Spielfeldrand?
    if x < 0 or x >= GAME_WIDTH:
        return True
    if y < 0 or y >= GAME_HEIGHT:
        return True

    # Kollision mit sich selbst?
    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True
    return False


def game_over():
    global restart_button
    canvas.delete("all")
    gap = 100  # Vertikaler Abstand, sodass die Bildschirmmitte genau zwischen Game Over-Text und Button liegt
    game_over_y = GAME_HEIGHT / 2 - gap / 1.5
    restart_y = GAME_HEIGHT / 2 + gap / 1.5

    canvas.create_text(
        GAME_WIDTH / 2,
        game_over_y,
        font=("consolas", 70),
        text="GAME OVER",
        fill="red",
    )
    restart_button = Button(
        window,
        text="Neu starten",
        font=("consolas", 40),
        command=reset_game,
        bg="#333333",
        fg=SNAKE_COLOR,
        bd=0,
        highlightthickness=0,
    )
    restart_button.bind("<Enter>", on_enter_button)
    restart_button.bind("<Leave>", on_leave_button)

    canvas.create_window(GAME_WIDTH / 2, restart_y, window=restart_button)


def reset_game():
    global score, direction, snake, food, restart_button
    if restart_button is not None:
        restart_button.destroy()
    score = 0
    direction = "down"
    canvas.delete("all")
    score_label.config(text="Score: {}".format(score))
    snake = Snake()
    food = Food()
    next_turn(snake, food)


def start_game():
    global start_button, snake, food, score, direction
    if start_button is not None:
        start_button.destroy()
    canvas.delete("all")
    score = 0
    direction = "down"
    score_label.config(text="Score: {}".format(score))
    snake = Snake()
    food = Food()
    next_turn(snake, food)


def show_start_screen():
    canvas.delete("all")
    canvas.create_text(
        GAME_WIDTH / 2,
        GAME_HEIGHT / 2 - 100,
        font=("consolas", 70),
        text="SNAKE",
        fill=SNAKE_COLOR,
    )
    global start_button
    start_button = Button(
        window,
        text="Start",
        font=("consolas", 40),
        command=start_game,
        bg="#333333",
        fg=SNAKE_COLOR,
        bd=0,
        highlightthickness=0,
    )
    start_button.bind("<Enter>", on_enter_button)
    start_button.bind("<Leave>", on_leave_button)
    canvas.create_window(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 50, window=start_button)


# --- Hover-Effekte für Buttons ---

def on_enter_button(event):
    event.widget.config(bg="#555555")


def on_leave_button(event):
    event.widget.config(bg="#333333")


# --- Hauptfenster und dynamische Anpassung der UI ---

window = Tk()
window.title("Snake Game")
window.attributes("-fullscreen", True)
window.configure(bg=BACKGROUND_COLOR)

# Bildschirmmaße ermitteln und Spielfeldgröße als Vielfaches von SPACE_SIZE berechnen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
control_frame_height = 80

GAME_WIDTH = (screen_width // SPACE_SIZE) * SPACE_SIZE
# Der obere Steuerbereich wird berücksichtigt
GAME_HEIGHT = ((screen_height - control_frame_height) // SPACE_SIZE) * SPACE_SIZE

# Steuerungsbereich oben (Score und Beenden-Button)
control_frame = Frame(window, bg=BACKGROUND_COLOR, height=control_frame_height)
control_frame.pack(fill=X)

score_label = Label(
    control_frame,
    text="Score: 0",
    font=("consolas", 30),
    bg=BACKGROUND_COLOR,
    fg=SNAKE_COLOR,
)
score_label.pack(side=LEFT, padx=20)

exit_button = Button(
    control_frame,
    text="Beenden",
    font=("consolas", 30),
    command=window.destroy,
    bg="#333333",
    fg=SNAKE_COLOR,
    bd=0,
    highlightthickness=0,
)
exit_button.pack(side=RIGHT, padx=20)
exit_button.bind("<Enter>", on_enter_button)
exit_button.bind("<Leave>", on_leave_button)

# Spielfeld (Canvas)
canvas = Canvas(
    window, bg=BACKGROUND_COLOR, width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0
)
canvas.pack()

# Tastenkürzel für die Schlangensteuerung
window.bind("<Left>", lambda event: change_direction("left"))
window.bind("<Right>", lambda event: change_direction("right"))
window.bind("<Up>", lambda event: change_direction("up"))
window.bind("<Down>", lambda event: change_direction("down"))

# Starte mit der Startseite (das Spiel beginnt erst, wenn man auf "Start" drückt)
show_start_screen()

window.mainloop()
