import random
import tkinter as tk
from tkinter import messagebox, simpledialog

class MinesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Mines Game")
        
        # Vollbildmodus beim Start aktivieren
        self.fullscreen_state = True
        self.root.attributes('-fullscreen', True)
        
        # Bildschirmabmessungen ermitteln
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Diagonale für Skalierungsfaktor berechnen
        self.screen_diagonal = (self.screen_width**2 + self.screen_height**2)**0.5
        self.scale_factor = self.screen_diagonal / 1920  # Basierend auf 1080p-Referenz
        
        self.root.configure(bg="#151c38")
        
        # Spielparameter
        self.grid_size = 5
        self.balance = 1000.0
        self.bet_amount = 0.0
        self.num_mines = 1  # Standardwert
        self.game_active = False
        self.revealed_tiles = set()
        self.mines_positions = set()
        self.current_multiplier = 1.0
        self.current_profit = 0.0
        self.credit_limit = 10000.0  # 10k Kredit-Maximum
        self.credit_taken = 0.0
        
        # Farben
        self.dark_blue = "#151c38"  # Dunkleres Blau wie im Original
        self.medium_blue = "#1e274e"  # Mittleres Blau für Panels
        self.light_blue = "#2d3875"
        self.highlight_blue = "#283159"  # Für Ränder
        self.diamond_color = "#2196F3"
        self.mine_color = "#FF5252"
        self.profit_color = "#4CAF50"
        self.bet_color = "#ffa500"
        
        # UI-Elemente basierend auf Bildschirmgröße skalieren
        self.scale_ui()
        
        # UI-Elemente erstellen
        self.create_header()
        self.create_info_panel()
        self.create_grid()
        self.create_controls()
        
        # Tasten für Vollbildmodus-Umschaltung und Fenstergrößenänderung binden
        self.bind_keys()
        
    def scale_ui(self):
        # Schriftgrößen basierend auf Bildschirmgröße
        self.base_font_size = int(12 * self.scale_factor)
        self.header_font_size = int(36 * self.scale_factor)
        self.button_font_size = int(14 * self.scale_factor)
        self.control_font_size = int(12 * self.scale_factor)
        
        # Verschiedene Schriftarten
        self.normal_font = ("Arial", self.base_font_size)
        self.bold_font = ("Arial", self.base_font_size, "bold")
        self.header_font = ("Arial", self.header_font_size, "italic")
        self.button_font = ("Arial", self.button_font_size, "bold")
        self.control_font = ("Arial", self.control_font_size)
        
        # Größen für UI-Elemente
        self.button_width = int(10 * self.scale_factor)
        self.button_height = int(5 * self.scale_factor)
        self.grid_padding = int(5 * self.scale_factor)
        self.panel_padding = int(15 * self.scale_factor)
        
    def bind_keys(self):
        # Escape-Taste zum Verlassen des Vollbildmodus
        self.root.bind("<Escape>", self.toggle_fullscreen)
        
        # F11 zum Umschalten des Vollbildmodus
        self.root.bind("<F11>", self.toggle_fullscreen)
        
        # Fenstergrößenänderung
        self.root.bind("<Configure>", self.handle_resize)
        
    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)
        # Wenn nicht im Vollbildmodus, Fenster maximieren
        if not self.fullscreen_state:
            self.root.state('zoomed')
            
    def handle_resize(self, event=None):
        # UI-Elemente basierend auf dem aktuellen Fenster aktualisieren
        if event and not self.fullscreen_state:  # Nur bei Größenänderung, wenn nicht im Vollbildmodus
            new_width = event.width
            new_height = event.height
            
            # Neuen Skalierungsfaktor berechnen
            new_diagonal = (new_width**2 + new_height**2)**0.5
            self.scale_factor = new_diagonal / 1920
            
            # UI-Elemente neu skalieren
            self.scale_ui()
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.dark_blue, height=int(80 * self.scale_factor))
        header_frame.pack(fill=tk.X, pady=(int(10 * self.scale_factor), int(20 * self.scale_factor)))
        
        # Rainbet-Logo im handgeschriebenen Stil
        logo_label = tk.Label(header_frame, text="Rainbet", font=self.header_font, 
                             fg="white", bg=self.dark_blue)
        logo_label.pack(side=tk.LEFT, padx=int(20 * self.scale_factor))
    
    def create_info_panel(self):
        info_frame = tk.Frame(self.root, bg=self.dark_blue)
        info_frame.pack(fill=tk.X, padx=int(20 * self.scale_factor), pady=int(10 * self.scale_factor))
        
        # Balance
        balance_frame = tk.Frame(info_frame, bg=self.medium_blue, 
                               padx=int(15 * self.scale_factor), pady=int(10 * self.scale_factor))
        balance_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, int(5 * self.scale_factor)))
        
        tk.Label(balance_frame, text="Balance", fg="#8888aa", bg=self.medium_blue, 
               font=self.control_font).pack(anchor="w")
        self.balance_display = tk.Label(balance_frame, text=f"${self.balance:.2f}", 
                                     font=("Arial", int(18 * self.scale_factor), "bold"), 
                                     fg="white", bg=self.medium_blue)
        self.balance_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
        # Credit info
        self.credit_display = tk.Label(balance_frame, text="", 
                                    font=("Arial", int(10 * self.scale_factor)), 
                                    fg="#FF9800", bg=self.medium_blue)
        self.credit_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
        # Bet/Profit
        bet_frame = tk.Frame(info_frame, bg=self.medium_blue, 
                           padx=int(15 * self.scale_factor), pady=int(10 * self.scale_factor))
        bet_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=int(5 * self.scale_factor))
        
        tk.Label(bet_frame, text="Bet amount/Profit", fg="#8888aa", bg=self.medium_blue, 
               font=self.control_font).pack(anchor="w")
        
        self.bet_display = tk.Label(bet_frame, text="$0.00", 
                                  font=("Arial", int(18 * self.scale_factor)), 
                                  fg=self.bet_color, bg=self.medium_blue)
        self.bet_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
        self.profit_display = tk.Label(bet_frame, text="$0.00", 
                                     font=("Arial", int(18 * self.scale_factor)), 
                                     fg=self.profit_color, bg=self.medium_blue)
        self.profit_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
        # Mines (nur Anzeige, keine Einstellung)
        mines_frame = tk.Frame(info_frame, bg=self.medium_blue, 
                             padx=int(15 * self.scale_factor), pady=int(10 * self.scale_factor))
        mines_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=int(5 * self.scale_factor))
        
        tk.Label(mines_frame, text="Mines", fg="#8888aa", bg=self.medium_blue, 
               font=self.control_font).pack(anchor="w")
        
        self.mines_display = tk.Label(mines_frame, text="1", 
                                    font=("Arial", int(18 * self.scale_factor), "bold"), 
                                    fg=self.mine_color, bg=self.medium_blue)
        self.mines_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
        # Multiplier
        multiplier_frame = tk.Frame(info_frame, bg=self.medium_blue, 
                                  padx=int(15 * self.scale_factor), pady=int(10 * self.scale_factor))
        multiplier_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(int(5 * self.scale_factor), 0))
        
        tk.Label(multiplier_frame, text="Multiplier", fg="#8888aa", bg=self.medium_blue, 
               font=self.control_font).pack(anchor="w")
        
        self.multiplier_display = tk.Label(multiplier_frame, text="1.00x", 
                                         font=("Arial", int(18 * self.scale_factor), "bold"), 
                                         fg="white", bg=self.medium_blue)
        self.multiplier_display.pack(anchor="w", pady=(int(5 * self.scale_factor), 0))
        
    def create_grid(self):
        grid_container = tk.Frame(self.root, bg=self.dark_blue, 
                                padx=int(20 * self.scale_factor), pady=int(20 * self.scale_factor))
        grid_container.pack(expand=True, fill=tk.BOTH, pady=int(20 * self.scale_factor))
        
        # Sicherstellen, dass der Grid-Container sich an Fenstergrößenänderungen anpasst
        grid_container.grid_rowconfigure(0, weight=1)
        grid_container.grid_columnconfigure(0, weight=1)
        
        self.grid_frame = tk.Frame(grid_container, bg=self.dark_blue)
        self.grid_frame.grid(row=0, column=0, sticky="nsew")
        
        # Alle Zeilen und Spalten im Grid gleichmäßig skalieren
        for i in range(self.grid_size):
            self.grid_frame.grid_rowconfigure(i, weight=1)
            self.grid_frame.grid_columnconfigure(i, weight=1)
        
        self.buttons = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                btn_frame = tk.Frame(self.grid_frame, bg=self.highlight_blue, 
                                   padx=1, pady=1)
                btn_frame.grid(row=i, column=j, padx=self.grid_padding, pady=self.grid_padding, sticky="nsew")
                
                # Frame konfigurieren, damit Button es ausfüllt
                btn_frame.grid_rowconfigure(0, weight=1)
                btn_frame.grid_columnconfigure(0, weight=1)
                
                # Verwende quadratische Buttons mit passendem Größenverhältnis wie im Original
                button = tk.Button(btn_frame, bg=self.medium_blue, 
                                 command=lambda r=i, c=j: self.reveal_tile(r, c),
                                 bd=0, highlightthickness=0, font=self.bold_font,
                                 activebackground=self.light_blue)
                button.grid(row=0, column=0, sticky="nsew")
                row.append(button)
            self.buttons.append(row)
    
    def create_controls(self):
        controls_frame = tk.Frame(self.root, bg=self.dark_blue, 
                                padx=int(20 * self.scale_factor), pady=int(10 * self.scale_factor))
        controls_frame.pack(fill=tk.X, pady=int(20 * self.scale_factor))
        
        # Bet Controls
        bet_controls = tk.Frame(controls_frame, bg=self.dark_blue)
        bet_controls.pack(side=tk.LEFT, anchor="w", expand=True, fill=tk.X)
        
        tk.Label(bet_controls, text="Einsatz:", fg="white", bg=self.dark_blue, 
               font=self.control_font).pack(anchor="w", pady=(0, int(5 * self.scale_factor)))
        
        bet_entry_frame = tk.Frame(bet_controls, bg=self.dark_blue)
        bet_entry_frame.pack(anchor="w", fill=tk.X, pady=(0, int(10 * self.scale_factor)))
        
        self.bet_entry = tk.Entry(bet_entry_frame, width=15, 
                                font=("Arial", int(14 * self.scale_factor)), 
                                bg=self.medium_blue, fg="white", 
                                bd=0, highlightthickness=1, highlightbackground=self.highlight_blue)
        self.bet_entry.pack(side=tk.LEFT, padx=(0, int(10 * self.scale_factor)))
        self.bet_entry.insert(0, "10.00")
        
        # Quick bet buttons
        for amount in ["5", "10", "25", "50", "100"]:
            btn = tk.Button(bet_entry_frame, text=amount, 
                          bg=self.medium_blue, fg="white", 
                          command=lambda a=amount: self.set_bet_amount(a),
                          bd=0, padx=int(10 * self.scale_factor), pady=int(3 * self.scale_factor), 
                          font=("Arial", int(10 * self.scale_factor)))
            btn.pack(side=tk.LEFT, padx=int(2 * self.scale_factor))
        
        # Mines selection - nur vordefinierte Optionen wie im Original
        mines_controls = tk.Frame(controls_frame, bg=self.dark_blue)
        mines_controls.pack(side=tk.LEFT, anchor="w", expand=True, fill=tk.X, pady=(int(20 * self.scale_factor), 0))
        
        tk.Label(mines_controls, text="Mines:", fg="white", bg=self.dark_blue, 
               font=self.control_font).pack(anchor="w", pady=(0, int(5 * self.scale_factor)))
        
        mines_options_frame = tk.Frame(mines_controls, bg=self.dark_blue)
        mines_options_frame.pack(anchor="w", fill=tk.X)
        
        # Vordefinierte Minenanzahl-Optionen
        for mines in ["1", "3", "5", "10", "24"]:
            btn = tk.Button(mines_options_frame, text=mines, 
                          bg=self.medium_blue, fg="white", 
                          command=lambda m=mines: self.set_mines_amount(m),
                          bd=0, padx=int(15 * self.scale_factor), pady=int(5 * self.scale_factor), 
                          font=("Arial", int(12 * self.scale_factor)))
            btn.pack(side=tk.LEFT, padx=int(5 * self.scale_factor))
        
        # Credit Button - NEU
        credit_frame = tk.Frame(self.root, bg=self.dark_blue, padx=int(20 * self.scale_factor))
        credit_frame.pack(fill=tk.X, pady=(0, int(10 * self.scale_factor)))
        
        self.credit_button = tk.Button(credit_frame, text="Kredit aufnehmen", 
                                     command=self.take_credit, 
                                     bg="#FF9800", fg="white", 
                                     font=("Arial", int(12 * self.scale_factor)),
                                     padx=int(10 * self.scale_factor), pady=int(5 * self.scale_factor), 
                                     bd=0)
        self.credit_button.pack(side=tk.LEFT)
        
        # Action Buttons
        action_frame = tk.Frame(self.root, bg=self.dark_blue, padx=int(20 * self.scale_factor))
        action_frame.pack(fill=tk.X, pady=int(10 * self.scale_factor))
        
        # Start Button
        self.start_button = tk.Button(action_frame, text="Start Game", 
                                    command=self.start_game, 
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", int(14 * self.scale_factor), "bold"),
                                    padx=int(20 * self.scale_factor), pady=int(10 * self.scale_factor), 
                                    bd=0)
        self.start_button.pack(side=tk.LEFT, padx=(0, int(10 * self.scale_factor)))
        
        # Cash Out Button
        self.cashout_button = tk.Button(action_frame, text="Cash Out", 
                                      command=self.cash_out, 
                                      bg="#FF9800", fg="white", 
                                      font=("Arial", int(14 * self.scale_factor), "bold"),
                                      padx=int(20 * self.scale_factor), pady=int(10 * self.scale_factor), 
                                      bd=0, state=tk.DISABLED)
        self.cashout_button.pack(side=tk.LEFT)
    
    def set_bet_amount(self, amount):
        self.bet_entry.delete(0, tk.END)
        self.bet_entry.insert(0, amount)
    
    def set_mines_amount(self, mines):
        self.num_mines = int(mines)
        self.mines_display.config(text=mines)
    
    def take_credit(self):
        """Kredit aufnehmen Funktion mit benutzerdefiniertem Betrag"""
        if self.credit_taken >= self.credit_limit:
            messagebox.showinfo("Kredit Limit", f"Sie haben bereits das maximale Kreditlimit von ${self.credit_limit:.2f} erreicht.")
            return
            
        available_credit = self.credit_limit - self.credit_taken
        
        # Benutzer nach Kreditbetrag fragen
        credit_amount_str = simpledialog.askstring("Kredit aufnehmen", 
                                               f"Wie viel Kredit möchten Sie aufnehmen?\nVerfügbar: ${available_credit:.2f}",
                                               parent=self.root)
        
        if credit_amount_str is None:  # Benutzer hat abgebrochen
            return
            
        try:
            credit_amount = float(credit_amount_str)
            
            if credit_amount <= 0:
                messagebox.showerror("Fehler", "Der Betrag muss größer als 0 sein.")
                return
                
            if credit_amount > available_credit:
                messagebox.showerror("Fehler", f"Der maximale verfügbare Kredit beträgt ${available_credit:.2f}.")
                return
                
            self.balance += credit_amount
            self.credit_taken += credit_amount
            
            self.balance_display.config(text=f"${self.balance:.2f}")
            self.credit_display.config(text=f"Kredit: ${self.credit_taken:.2f}")
            
            messagebox.showinfo("Kredit aufgenommen", 
                              f"Sie haben ${credit_amount:.2f} Kredit aufgenommen.\n"
                              f"Verbleibendes Kreditlimit: ${(self.credit_limit - self.credit_taken):.2f}")
                
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie einen gültigen Betrag ein.")
    
    def check_game_over(self):
        """Prüft, ob der Spieler pleite ist und das Spiel beendet werden sollte"""
        if self.balance <= 0 and (self.credit_limit - self.credit_taken) <= 0:
            messagebox.showinfo("GAME OVER", 
                             "Du hast dein gesamtes Geld verloren und kannst keinen weiteren Kredit aufnehmen.\n"
                             "Das Spiel ist zu Ende!")
            self.reset_game()
            return True
        return False
    
    def reset_game(self):
        """Setzt das Spiel auf Anfangswerte zurück"""
        self.balance = 1000.0
        self.credit_taken = 0.0
        self.balance_display.config(text=f"${self.balance:.2f}")
        self.credit_display.config(text="")
        self.bet_display.config(text="$0.00")
        self.profit_display.config(text="$0.00")
        self.current_multiplier = 1.0
        self.multiplier_display.config(text="1.00x")
        
        # Alle Buttons zurücksetzen
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.buttons[i][j].config(text="", bg=self.medium_blue, state=tk.NORMAL)
    
    def calculate_multiplier(self, revealed_count):
        """
        Berechnet den Multiplikator basierend auf der Anzahl der aufgedeckten Felder
        und der gewählten Minenanzahl.
        """
        total_tiles = self.grid_size * self.grid_size
        safe_tiles = total_tiles - self.num_mines
        
        if revealed_count == 0:
            return 1.0
        
        # Wahrscheinlichkeitsberechnung
        probability = 1.0
        for i in range(revealed_count):
            safe_remaining = safe_tiles - i
            total_remaining = total_tiles - i
            probability *= safe_remaining / total_remaining
            
        # Hausvorteils-Faktor
        house_edge = 0.95  # 5% Hausvorteil
        return (1 / probability) * house_edge
    
    def start_game(self):
        try:
            self.bet_amount = float(self.bet_entry.get())
            
            if self.bet_amount <= 0:
                messagebox.showerror("Fehler", "Der Einsatz muss größer als 0 sein")
                return
                
            if self.bet_amount > self.balance:
                messagebox.showerror("Fehler", "Unzureichendes Guthaben")
                return
                
            # Einsatz vom Guthaben abziehen
            self.balance -= self.bet_amount
            self.balance_display.config(text=f"${self.balance:.2f}")
            self.bet_display.config(text=f"${self.bet_amount:.2f}")
            self.profit_display.config(text="$0.00")
            
            # Prüfen, ob der Spieler nach diesem Einsatz pleite ist
            if self.check_game_over():
                return
                
            # Spielstatus zurücksetzen
            self.game_active = True
            self.revealed_tiles = set()
            self.current_multiplier = 1.0
            self.current_profit = 0.0
            self.multiplier_display.config(text=f"{self.current_multiplier:.2f}x")
            
            # Alle Buttons zurücksetzen
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    self.buttons[i][j].config(text="", bg=self.medium_blue, state=tk.NORMAL)
            
            # Minen zufällig platzieren
            self.mines_positions = set()
            while len(self.mines_positions) < self.num_mines:
                pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
                self.mines_positions.add(pos)
                
            # Cash Out Button aktivieren
            self.cashout_button.config(state=tk.NORMAL)
            # Start Button während des Spiels deaktivieren
            self.start_button.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gültige Zahlen eingeben")
    
    def reveal_tile(self, row, col):
        if not self.game_active or (row, col) in self.revealed_tiles:
            return
            
        self.revealed_tiles.add((row, col))
        
        if (row, col) in self.mines_positions:
            # Mine getroffen - Game Over
            self.buttons[row][col].config(text="💣", bg=self.mine_color)
            self.game_over(False)
        else:
            # Diamant gefunden
            self.buttons[row][col].config(text="💎", bg=self.diamond_color)
            
            # Multiplikator und Gewinn aktualisieren
            revealed_count = len(self.revealed_tiles)
            new_multiplier = self.calculate_multiplier(revealed_count)
            
            # Animation für Multiplikator-Erhöhung
            self.animate_multiplier(self.current_multiplier, new_multiplier)
            self.current_multiplier = new_multiplier
            
            # Aktuellen potenziellen Gewinn berechnen
            self.current_profit = self.bet_amount * self.current_multiplier - self.bet_amount
            self.profit_display.config(text=f"${self.current_profit:.2f}")
            
            # Prüfen, ob alle sicheren Felder aufgedeckt wurden (Gewinnbedingung)
            safe_tiles = self.grid_size * self.grid_size - self.num_mines
            if revealed_count == safe_tiles:
                self.game_over(True)
    
    def animate_multiplier(self, start_value, end_value, step=10):
        """Animiert die Erhöhung des Multiplikators"""
        if step <= 0 or abs(start_value - end_value) < 0.01:
            self.multiplier_display.config(text=f"{end_value:.2f}x")
            return
            
        # Interpolierter Wert
        current = start_value + (end_value - start_value) * (1 - step/10)
        self.multiplier_display.config(text=f"{current:.2f}x")
        
        # Nächsten Schritt planen
        self.root.after(50, lambda: self.animate_multiplier(start_value, end_value, step-1))
    
    def cash_out(self):
        if not self.game_active:
            return
            
        # Gewinn zum Guthaben hinzufügen
        cash_out_amount = self.bet_amount + self.current_profit
        self.balance += cash_out_amount
        self.balance_display.config(text=f"${self.balance:.2f}")
        
        # Zeigen, wo die Minen waren
        for row, col in self.mines_positions:
            if (row, col) not in self.revealed_tiles:
                self.buttons[row][col].config(text="💣", bg=self.mine_color)
        
        messagebox.showinfo("Cash Out", f"Du hast ${self.current_profit:.2f} Gewinn ausgezahlt!")
        self.game_active = False
        self.cashout_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
    
    def game_over(self, won):
        self.game_active = False
        
        # Alle Minen zeigen
        for row, col in self.mines_positions:
            if (row, col) not in self.revealed_tiles:
                self.buttons[row][col].config(text="💣", bg=self.mine_color)
        
        if won:
            win_amount = self.bet_amount + self.current_profit
            messagebox.showinfo("Glückwunsch", f"Du hast ${self.current_profit:.2f} gewonnen!")
            self.balance += win_amount
            self.balance_display.config(text=f"${self.balance:.2f}")
        else:
            messagebox.showinfo("Game Over", "Du hast eine Mine getroffen und deinen Einsatz verloren!")
            
            # Nach Verlust prüfen, ob der Spieler pleite ist
            self.check_game_over()
        
        self.cashout_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

# Spiel starten
if __name__ == "__main__":
    root = tk.Tk()
    
    # DPI-Skalierung unter Windows behandeln
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    game = MinesGame(root)
    root.mainloop()
