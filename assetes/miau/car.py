import tkinter as tk
from tkinter import messagebox, ttk
import random

cars = [
    {"name": "Ford Mustang", "type": "Sportwagen", "fuel": "Benzin", "origin": "USA", "year": 2022, "brand": "Ford", "drive": "Heck", "power": 450, "price": 50000, "color": "Rot", "seats": 4},
    {"name": "Tesla Model 3", "type": "Elektroauto", "fuel": "Elektro", "origin": "USA", "year": 2023, "brand": "Tesla", "drive": "Allrad", "power": 283, "price": 45000, "color": "Weiß", "seats": 5},
    {"name": "Toyota Corolla", "type": "Limousine", "fuel": "Benzin", "origin": "Japan", "year": 2021, "brand": "Toyota", "drive": "Front", "power": 132, "price": 25000, "color": "Silber", "seats": 5},
    {"name": "Volkswagen Golf", "type": "Kompaktwagen", "fuel": "Diesel", "origin": "Deutschland", "year": 2022, "brand": "Volkswagen", "drive": "Front", "power": 150, "price": 30000, "color": "Blau", "seats": 5},
    {"name": "BMW i3", "type": "Elektroauto", "fuel": "Elektro", "origin": "Deutschland", "year": 2021, "brand": "BMW", "drive": "Heck", "power": 170, "price": 40000, "color": "Schwarz", "seats": 4},
    {"name": "Porsche 911", "type": "Sportwagen", "fuel": "Benzin", "origin": "Deutschland", "year": 2023, "brand": "Porsche", "drive": "Allrad", "power": 450, "price": 120000, "color": "Gelb", "seats": 2},
]

class AutoRateSpiel:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto-Rate-Spiel")
        self.master.geometry("600x700")
        self.master.configure(bg="#2C2C2C")

        self.car_to_guess = None
        self.hints = []
        self.current_hint = 0
        self.score = 0
        self.total_score = 0
        self.attempts = 0
        self.max_attempts = 7
        self.difficulty = "Mittel"
        self.initial_hints = {"Leicht": 4, "Mittel": 3, "Schwer": 2}
        self.max_points = {"Leicht": 7, "Mittel": 12, "Schwer": 17}

        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        tk.Label(self.master, text="Auto-Rate-Spiel", font=("Arial", 20, "bold"), bg="#2C2C2C", fg="#FF0000").pack(pady=20)

        self.difficulty_var = tk.StringVar(value="Mittel")
        tk.Label(self.master, text="Schwierigkeit:", bg="#2C2C2C", fg="#FFFFFF").pack()
        ttk.Combobox(self.master, textvariable=self.difficulty_var, values=["Leicht", "Mittel", "Schwer"], state="readonly").pack(pady=5)

        self.hint_label = tk.Label(self.master, text="", font=("Arial", 12), bg="#2C2C2C", fg="#FFFFFF", wraplength=550)
        self.hint_label.pack(pady=10)

        self.guess_entry = tk.Entry(self.master, font=("Arial", 12))
        self.guess_entry.pack(pady=10)

        self.guess_button = tk.Button(self.master, text="Raten", command=self.make_guess, bg="#FF0000", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.guess_button.pack(pady=10)

        self.next_hint_button = tk.Button(self.master, text="Nächster Hinweis", command=self.show_next_hint, bg="#FF0000", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.next_hint_button.pack(pady=10)

        self.new_game_button = tk.Button(self.master, text="Neues Spiel", command=self.new_game, bg="#FF0000", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.new_game_button.pack(pady=10)

        self.score_label = tk.Label(self.master, text="Punkte: 0", font=("Arial", 12), bg="#2C2C2C", fg="#FFFFFF")
        self.score_label.pack(pady=5)

        self.total_score_label = tk.Label(self.master, text="Gesamtpunkte: 0", font=("Arial", 12), bg="#2C2C2C", fg="#FFFFFF")
        self.total_score_label.pack(pady=5)

        self.attempts_label = tk.Label(self.master, text="Versuche: 0/7", font=("Arial", 12), bg="#2C2C2C", fg="#FFFFFF")
        self.attempts_label.pack(pady=5)

    def new_game(self):
        self.difficulty = self.difficulty_var.get()
        self.car_to_guess = random.choice(cars)
        self.hints = [
            f"Dieses Auto ist ein {self.car_to_guess['type']}.",
            f"Es fährt mit {self.car_to_guess['fuel']}.",
            f"Das Auto kommt aus {self.car_to_guess['origin']}.",
            f"Es wurde im Jahr {self.car_to_guess['year']} gebaut.",
            f"Die Marke ist {self.car_to_guess['brand']}.",
            f"Es hat {self.car_to_guess['drive']}antrieb.",
            f"Die Leistung beträgt {self.car_to_guess['power']} PS.",
            f"Der Preis liegt bei {self.car_to_guess['price']} €.",
            f"Die Farbe des Autos ist {self.car_to_guess['color']}.",
            f"Es hat {self.car_to_guess['seats']} Sitzplätze."
        ]
        random.shuffle(self.hints)
        self.current_hint = 0
        self.attempts = 0
        self.score = self.max_points[self.difficulty]
        self.update_labels()
        
        initial_hints = self.initial_hints[self.difficulty]
        hint_text = "Starthinweise:\n"
        for i in range(initial_hints):
            hint_text += f"{i+1}. {self.hints[i]}\n"
        self.current_hint = initial_hints
        
        self.hint_label.config(text=hint_text)
        self.guess_entry.delete(0, tk.END)

    def show_next_hint(self):
        if self.current_hint < len(self.hints):
            self.hint_label.config(text=f"{self.hint_label.cget('text')}\n{self.current_hint + 1}. {self.hints[self.current_hint]}")
            self.current_hint += 1
            self.score = max(0, self.score - 1)
            self.update_labels()
        else:
            messagebox.showinfo("Keine Hinweise mehr", "Es gibt keine weiteren Hinweise. Versuche zu raten!")

    def make_guess(self):
        guess = self.guess_entry.get().strip().lower()
        self.attempts += 1

        if guess == self.car_to_guess['name'].lower():
            self.total_score += self.score
            self.update_labels()
            messagebox.showinfo("Richtig!", f"Glückwunsch! Du hast das Auto richtig erraten: {self.car_to_guess['name']}\nDu erhältst {self.score} Punkte!")
            self.new_game()
        else:
            if self.attempts >= self.max_attempts:
                messagebox.showinfo("Spiel vorbei", f"Leider hast du alle Versuche aufgebraucht.\n\nDie Lösung war: {self.car_to_guess['name']}\n\nDetails:\nTyp: {self.car_to_guess['type']}\nMarke: {self.car_to_guess['brand']}\nHerkunft: {self.car_to_guess['origin']}\nBaujahr: {self.car_to_guess['year']}\nTreibstoff: {self.car_to_guess['fuel']}\nAntrieb: {self.car_to_guess['drive']}\nLeistung: {self.car_to_guess['power']} PS\nPreis: {self.car_to_guess['price']} €\nFarbe: {self.car_to_guess['color']}\nSitzplätze: {self.car_to_guess['seats']}")
                self.new_game()
            else:
                messagebox.showinfo("Falsch", "Das ist leider nicht richtig. Versuche es noch einmal oder fordere einen weiteren Hinweis an.")
        
        self.update_labels()

    def update_labels(self):
        self.score_label.config(text=f"Punkte: {self.score}")
        self.total_score_label.config(text=f"Gesamtpunkte: {self.total_score}")
        self.attempts_label.config(text=f"Versuche: {self.attempts}/{self.max_attempts}")

root = tk.Tk()
game = AutoRateSpiel(root)
root.mainloop()
