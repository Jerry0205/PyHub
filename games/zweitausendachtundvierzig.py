import pygame
import random
import math

# Pygame initialisieren
pygame.init()

# Framerate und Spielfeldgröße
FPS = 60
BREITE, HOEHE = 800, 800
ZEILEN = 4
SPALTEN = 4

# Rechteckgröße
RECHTECK_HOEHE = HOEHE // ZEILEN
RECHTECK_BREITE = BREITE // SPALTEN

# Farben und Schriftarten
RAND_FARBE = (187, 173, 160)
RAND_DICKE = 10
HINTERGRUND_FARBE = (205, 192, 180)
SCHRIFT_FARBE = (119, 110, 101)
SCHRIFT = pygame.font.SysFont("comicsans", 60, bold=True)
BEWEGUNGS_GESCHWINDIGKEIT = 20

# Fenster erstellen
FENSTER = pygame.display.set_mode((BREITE, HOEHE))
pygame.display.set_caption("2048")

class Kachel:
    FARBEN = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, wert, zeile, spalte):
        self.wert = wert
        self.zeile = zeile
        self.spalte = spalte
        self.x = spalte * RECHTECK_BREITE
        self.y = zeile * RECHTECK_HOEHE

    def farbe_holen(self):
        # Farbe basierend auf dem Wert der Kachel auswählen
        farb_index = int(math.log2(self.wert)) - 1
        return self.FARBEN[farb_index]

    def zeichnen(self, fenster):
        # Kachel zeichnen
        farbe = self.farbe_holen()
        pygame.draw.rect(fenster, farbe, (self.x, self.y, RECHTECK_BREITE, RECHTECK_HOEHE))
        # Wert der Kachel rendern und zentrieren
        text = SCHRIFT.render(str(self.wert), 1, SCHRIFT_FARBE)
        fenster.blit(
            text,
            (
                self.x + (RECHTECK_BREITE / 2 - text.get_width() / 2),
                self.y + (RECHTECK_HOEHE / 2 - text.get_height() / 2),
            ),
        )

    def position_setzen(self, ceil=False):
        # Position der Kachel basierend auf x und y aktualisieren
        if ceil:
            self.zeile = math.ceil(self.y / RECHTECK_HOEHE)
            self.spalte = math.ceil(self.x / RECHTECK_BREITE)
        else:
            self.zeile = math.floor(self.y / RECHTECK_HOEHE)
            self.spalte = math.floor(self.x / RECHTECK_BREITE)

    def bewegen(self, delta):
        # Kachel verschieben
        self.x += delta[0]
        self.y += delta[1]


def raster_zeichnen(fenster):
    # Rasterlinien zeichnen
    for zeile in range(1, ZEILEN):
        y = zeile * RECHTECK_HOEHE
        pygame.draw.line(fenster, RAND_FARBE, (0, y), (BREITE, y), RAND_DICKE)

    for spalte in range(1, SPALTEN):
        x = spalte * RECHTECK_BREITE
        pygame.draw.line(fenster, RAND_FARBE, (x, 0), (x, HOEHE), RAND_DICKE)

    # Rahmen zeichnen
    pygame.draw.rect(fenster, RAND_FARBE, (0, 0, BREITE, HOEHE), RAND_DICKE)


def zeichnen(fenster, kacheln):
    # Hintergrund zeichnen
    fenster.fill(HINTERGRUND_FARBE)

    # Alle Kacheln zeichnen
    for kachel in kacheln.values():
        kachel.zeichnen(fenster)

    # Raster zeichnen
    raster_zeichnen(fenster)

    # Aktualisieren
    pygame.display.update()


def zufaellige_position(kacheln):
    # Zufällige freie Position für eine neue Kachel finden
    while True:
        zeile = random.randrange(0, ZEILEN)
        spalte = random.randrange(0, SPALTEN)
        if f"{zeile}{spalte}" not in kacheln:
            break
    return zeile, spalte


def kacheln_bewegen(fenster, kacheln, uhr, richtung):
    aktualisiert = True
    blockierte_kacheln = set()

    # Bewegungslogik basierend auf der Richtung definieren
    if richtung == "links":
        sortier_funktion = lambda x: x.spalte
        umgekehrt = False
        delta = (-BEWEGUNGS_GESCHWINDIGKEIT, 0)
        rand_check = lambda kachel: kachel.spalte == 0
        naechste_kachel = lambda kachel: kacheln.get(f"{kachel.zeile}{kachel.spalte - 1}")
        zusammenfuegen_check = lambda kachel, nk: kachel.x > nk.x + BEWEGUNGS_GESCHWINDIGKEIT
        bewegen_check = (
            lambda kachel, nk: kachel.x > nk.x + RECHTECK_BREITE + BEWEGUNGS_GESCHWINDIGKEIT
        )
        ceil = True
    elif richtung == "rechts":
        sortier_funktion = lambda x: x.spalte
        umgekehrt = True
        delta = (BEWEGUNGS_GESCHWINDIGKEIT, 0)
        rand_check = lambda kachel: kachel.spalte == SPALTEN - 1
        naechste_kachel = lambda kachel: kacheln.get(f"{kachel.zeile}{kachel.spalte + 1}")
        zusammenfuegen_check = lambda kachel, nk: kachel.x < nk.x - BEWEGUNGS_GESCHWINDIGKEIT
        bewegen_check = (
            lambda kachel, nk: kachel.x + RECHTECK_BREITE + BEWEGUNGS_GESCHWINDIGKEIT < nk.x
        )
        ceil = False
    elif richtung == "oben":
        sortier_funktion = lambda x: x.zeile
        umgekehrt = False
        delta = (0, -BEWEGUNGS_GESCHWINDIGKEIT)
        rand_check = lambda kachel: kachel.zeile == 0
        naechste_kachel = lambda kachel: kacheln.get(f"{kachel.zeile - 1}{kachel.spalte}")
        zusammenfuegen_check = lambda kachel, nk: kachel.y > nk.y + BEWEGUNGS_GESCHWINDIGKEIT
        bewegen_check = (
            lambda kachel, nk: kachel.y > nk.y + RECHTECK_HOEHE + BEWEGUNGS_GESCHWINDIGKEIT
        )
        ceil = True
    elif richtung == "unten":
        sortier_funktion = lambda x: x.zeile
        umgekehrt = True
        delta = (0, BEWEGUNGS_GESCHWINDIGKEIT)
        rand_check = lambda kachel: kachel.zeile == ZEILEN - 1
        naechste_kachel = lambda kachel: kacheln.get(f"{kachel.zeile + 1}{kachel.spalte}")
        zusammenfuegen_check = lambda kachel, nk: kachel.y < nk.y - BEWEGUNGS_GESCHWINDIGKEIT
        bewegen_check = (
            lambda kachel, nk: kachel.y + RECHTECK_HOEHE + BEWEGUNGS_GESCHWINDIGKEIT < nk.y
        )
        ceil = False

    while aktualisiert:
        uhr.tick(FPS)
        aktualisiert = False
        sortierte_kacheln = sorted(kacheln.values(), key=sortier_funktion, reverse=umgekehrt)

        for i, kachel in enumerate(sortierte_kacheln):
            if rand_check(kachel):
                continue

            nk = naechste_kachel(kachel)
            if not nk:
                kachel.bewegen(delta)
            elif (
                kachel.wert == nk.wert
                and kachel not in blockierte_kacheln
                and nk not in blockierte_kacheln
            ):
                if zusammenfuegen_check(kachel, nk):
                    kachel.bewegen(delta)
                else:
                    nk.wert *= 2
                    sortierte_kacheln.pop(i)
                    blockierte_kacheln.add(nk)
            elif bewegen_check(kachel, nk):
                kachel.bewegen(delta)
            else:
                continue

            kachel.position_setzen(ceil)
            aktualisiert = True

        kacheln_aktualisieren(fenster, kacheln, sortierte_kacheln)

    return bewegung_beenden(kacheln)


def bewegung_beenden(kacheln):
    # Prüfen, ob das Spiel vorbei ist
    if len(kacheln) == ZEILEN * SPALTEN:
        return "verloren"

    # Neue zufällige Kachel hinzufügen
    zeile, spalte = zufaellige_position(kacheln)
    kacheln[f"{zeile}{spalte}"] = Kachel(random.choice([2, 4]), zeile, spalte)
    return "weiter"


def kacheln_aktualisieren(fenster, kacheln, sortierte_kacheln):
    # Kachel-Dictionary aktualisieren
    kacheln.clear()
    for kachel in sortierte_kacheln:
        kacheln[f"{kachel.zeile}{kachel.spalte}"] = kachel

    # Neu zeichnen
    zeichnen(fenster, kacheln)


def kacheln_generieren():
    # Startkacheln generieren
    kacheln = {}
    for _ in range(2):
        zeile, spalte = zufaellige_position(kacheln)
        kacheln[f"{zeile}{spalte}"] = Kachel(2, zeile, spalte)

    return kacheln


def spiel_menue(fenster):
    # Menü nach dem Game Over anzeigen
    fenster.fill(HINTERGRUND_FARBE)

    titel = SCHRIFT.render("Game Over", 1, SCHRIFT_FARBE)
    fenster.blit(
        titel, (BREITE // 2 - titel.get_width() // 2, HOEHE // 3 - titel.get_height() // 2)
    )

    optionen = ["Play Again", "Quit"]
    ausgewaehlt = 0

    while True:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                quit()

            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == pygame.K_UP:
                    ausgewaehlt = (ausgewaehlt - 1) % len(optionen)
                if ereignis.key == pygame.K_DOWN:
                    ausgewaehlt = (ausgewaehlt + 1) % len(optionen)
                if ereignis.key == pygame.K_RETURN:
                    return ausgewaehlt

        # Menüoptionen zeichnen
        fenster.fill(HINTERGRUND_FARBE)
        fenster.blit(titel, (BREITE // 2 - titel.get_width() // 2, HOEHE // 3 - titel.get_height() // 2))

        for i, option in enumerate(optionen):
            farbe = (0, 0, 0) if i == ausgewaehlt else SCHRIFT_FARBE
            text = SCHRIFT.render(option, 1, farbe)
            fenster.blit(text, (BREITE // 2 - text.get_width() // 2, HOEHE // 2 + i * 60))

        pygame.display.update()


def hauptspiel(fenster):
    uhr = pygame.time.Clock()
    laufend = True

    # Kacheln initial generieren
    kacheln = kacheln_generieren()

    while laufend:
        uhr.tick(FPS)

        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                laufend = False
                break

            # Pfeiltasten verarbeiten
            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == pygame.K_LEFT:
                    ergebnis = kacheln_bewegen(fenster, kacheln, uhr, "links")
                if ereignis.key == pygame.K_RIGHT:
                    ergebnis = kacheln_bewegen(fenster, kacheln, uhr, "rechts")
                if ereignis.key == pygame.K_UP:
                    ergebnis = kacheln_bewegen(fenster, kacheln, uhr, "oben")
                if ereignis.key == pygame.K_DOWN:
                    ergebnis = kacheln_bewegen(fenster, kacheln, uhr, "unten")

                if ergebnis == "verloren":
                    auswahl = spiel_menue(fenster)
                    if auswahl == 0:  # "Play Again"
                        hauptspiel(fenster)
                    elif auswahl == 1:  # "Quit"
                        laufend = False

        # Spiel zeichnen
        zeichnen(fenster, kacheln)

    pygame.quit()
def spiel_menue(fenster):
    # Menü nach dem Game Over anzeigen
    fenster.fill(HINTERGRUND_FARBE)

    titel = SCHRIFT.render("Game Over", 1, SCHRIFT_FARBE)
    fenster.blit(
        titel, (BREITE // 2 - titel.get_width() // 2, HOEHE // 3 - titel.get_height() // 2)
    )

    optionen = ["Play Again", "Quit"]
    ausgewaehlt = -1

    optionen_positionen = []
    for i, option in enumerate(optionen):
        text = SCHRIFT.render(option, 1, SCHRIFT_FARBE)
        x = BREITE // 2 - text.get_width() // 2
        y = HOEHE // 2 + i * 60
        optionen_positionen.append((x, y, text.get_width(), text.get_height()))

    while True:
        maus_x, maus_y = pygame.mouse.get_pos()
        ausgewaehlt = -1  # Reset selection

        for i, (x, y, breite, hoehe) in enumerate(optionen_positionen):
            if x <= maus_x <= x + breite and y <= maus_y <= y + hoehe:
                ausgewaehlt = i
                break

        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                quit()

            if ereignis.type == pygame.KEYDOWN:
                if ereignis.key == pygame.K_UP:
                    ausgewaehlt = (ausgewaehlt - 1) % len(optionen)
                if ereignis.key == pygame.K_DOWN:
                    ausgewaehlt = (ausgewaehlt + 1) % len(optionen)
                if ereignis.key == pygame.K_RETURN and ausgewaehlt != -1:
                    return ausgewaehlt

            if ereignis.type == pygame.MOUSEBUTTONDOWN and ausgewaehlt != -1:
                return ausgewaehlt

        # Menüoptionen zeichnen
        fenster.fill(HINTERGRUND_FARBE)
        fenster.blit(titel, (BREITE // 2 - titel.get_width() // 2, HOEHE // 3 - titel.get_height() // 2))

        for i, option in enumerate(optionen):
            farbe = (0, 0, 0) if i == ausgewaehlt else SCHRIFT_FARBE
            text = SCHRIFT.render(option, 1, farbe)
            fenster.blit(text, (optionen_positionen[i][0], optionen_positionen[i][1]))

        pygame.display.update()

if __name__ == "__main__":
    hauptspiel(FENSTER)