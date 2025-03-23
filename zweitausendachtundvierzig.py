import os
import json
import pygame
import random
import math

# -------------------------------
# Konfiguration aus config.json laden
# -------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Wenn dark_mode true ist, dann Dark Mode, ansonsten With Mode
MODE = "dark" if config.get("dark_mode", True) else "with"

# -------------------------------
# Initialisierung und Konstanten
# -------------------------------
pygame.init()
FPS = 60

# Raster-Größe (4x4)
ZEILEN, SPALTEN = 4, 4

# Ränder oder Linienbreite festlegen
RAND_DICKE = 10

# Farbkonstruktion basierend auf dem Modus
if MODE == "dark":
    RAND_FARBE = (50, 50, 50)
    HINTERGRUND_FARBE = (30, 30, 30)
    SCHRIFT_FARBE = (255, 255, 255)
    KACHEL_FARBEN = [
        (40, 40, 40),    # für 2
        (60, 60, 60),    # für 4
        (80, 80, 80),    # für 8
        (100, 100, 100),  # für 16
        (120, 120, 120),  # für 32
        (140, 140, 140),  # für 64
        (160, 160, 160),  # für 128
        (180, 180, 180),  # für 256
        (200, 200, 200),  # für 512
        (220, 220, 220),  # für 1024
        (240, 240, 240)   # für 2048
    ]
else:  # With Mode (heller Modus)
    RAND_FARBE = (200, 200, 200)
    HINTERGRUND_FARBE = (245, 245, 245)
    SCHRIFT_FARBE = (0, 0, 0)
    KACHEL_FARBEN = [
        (238, 228, 218),  # für 2
        (237, 224, 200),  # für 4
        (242, 177, 121),  # für 8
        (245, 149, 99),   # für 16
        (246, 124, 95),   # für 32
        (246, 94, 59),    # für 64
        (237, 207, 114),  # für 128
        (237, 204, 97),   # für 256
        (237, 200, 80),   # für 512
        (237, 197, 63),   # für 1024
        (237, 194, 46)    # für 2048
    ]

# -------------------------------
# Weitere Konfigurationen
# -------------------------------
info = pygame.display.Info()
DISPLAY_WIDTH, DISPLAY_HEIGHT = info.current_w, info.current_h
FENSTER = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("2048 - " + ("Dark Mode" if MODE == "dark" else "With Mode"))

board_candidate = int(0.8 * min(DISPLAY_WIDTH, DISPLAY_HEIGHT))
BOARD_SIZE = (board_candidate // SPALTEN) * SPALTEN
OFFSET_X = (DISPLAY_WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (DISPLAY_HEIGHT - BOARD_SIZE) // 2

BREITE = HOEHE = BOARD_SIZE
RECHTECK_BREITE = BOARD_SIZE // SPALTEN
RECHTECK_HOEHE = BOARD_SIZE // ZEILEN

FONT_SIZE = RECHTECK_BREITE // 3
SCHRIFT = pygame.font.SysFont("comicsans", FONT_SIZE, bold=True)

# -------------------------------
# Klasse: Kachel
# -------------------------------
class Kachel:
    """
    Eine Kachel besitzt ihren Wert, die logische (Gitter-)Position (zeile, spalte)
    sowie die aktuelle Pixelposition (x, y). target_x und target_y geben die Zielposition 
    während der Animation an.
    """
    FARBEN = KACHEL_FARBEN

    def __init__(self, wert, zeile, spalte):
        self.wert = wert
        self.zeile = zeile
        self.spalte = spalte
        self.x = spalte * RECHTECK_BREITE
        self.y = zeile * RECHTECK_HOEHE
        self.target_x = self.x
        self.target_y = self.y

    def farbe_holen(self):
        index = int(math.log2(self.wert)) - 1
        if index < len(self.FARBEN):
            return self.FARBEN[index]
        return self.FARBEN[-1]

    def zeichnen(self, oberflaeche):
        farbe = self.farbe_holen()
        rect = pygame.Rect(
            self.x + OFFSET_X,
            self.y + OFFSET_Y,
            RECHTECK_BREITE,
            RECHTECK_HOEHE,
        )
        pygame.draw.rect(oberflaeche, farbe, rect)
        text = SCHRIFT.render(str(self.wert), True, SCHRIFT_FARBE)
        text_x = self.x + OFFSET_X + (RECHTECK_BREITE - text.get_width()) // 2
        text_y = self.y + OFFSET_Y + (RECHTECK_HOEHE - text.get_height()) // 2
        oberflaeche.blit(text, (text_x, text_y))

# -------------------------------
# Zeichen- und Hilfsfunktionen
# -------------------------------
def raster_zeichnen(oberflaeche):
    for zeile in range(1, ZEILEN):
        y = zeile * RECHTECK_HOEHE + OFFSET_Y
        pygame.draw.line(
            oberflaeche,
            RAND_FARBE,
            (OFFSET_X, y),
            (OFFSET_X + BREITE, y),
            RAND_DICKE,
        )
    for spalte in range(1, SPALTEN):
        x = spalte * RECHTECK_BREITE + OFFSET_X
        pygame.draw.line(
            oberflaeche,
            RAND_FARBE,
            (x, OFFSET_Y),
            (x, OFFSET_Y + HOEHE),
            RAND_DICKE,
        )
    pygame.draw.rect(oberflaeche, RAND_FARBE, (OFFSET_X, OFFSET_Y, BREITE, HOEHE), RAND_DICKE)

def zeichnen(oberflaeche, kacheln):
    if not pygame.display.get_surface():
        return
    oberflaeche.fill(HINTERGRUND_FARBE)
    for tile in kacheln.values():
        tile.zeichnen(oberflaeche)
    raster_zeichnen(oberflaeche)
    pygame.display.update()

def zufaellige_position(kacheln):
    while True:
        zeile = random.randrange(0, ZEILEN)
        spalte = random.randrange(0, SPALTEN)
        if f"{zeile}{spalte}" not in kacheln:
            return zeile, spalte

def erstelle_gitter_aus_kacheln(kacheln):
    gitter = [[None for _ in range(SPALTEN)] for _ in range(ZEILEN)]
    for tile in kacheln.values():
        gitter[tile.zeile][tile.spalte] = tile
    return gitter

# -------------------------------
# Merge- und Bewegungsfunktionen (Neuer Ansatz)
# Es werden pro Zeile/Spalte neue Kachelobjekte erstellt, sodass beim Zusammenführen
# keine Referenzen verloren gehen.
# -------------------------------
def bewege_links(kacheln):
    gitter = erstelle_gitter_aus_kacheln(kacheln)
    neues_gitter = [[None for _ in range(SPALTEN)] for _ in range(ZEILEN)]
    for zeile in range(ZEILEN):
        zeilen_kacheln = [tile for tile in gitter[zeile] if tile is not None]
        zusammengeführt = []
        i = 0
        while i < len(zeilen_kacheln):
            if i + 1 < len(zeilen_kacheln) and zeilen_kacheln[i].wert == zeilen_kacheln[i + 1].wert:
                neuer_wert = zeilen_kacheln[i].wert * 2
                neuer_tile = Kachel(neuer_wert, zeile, 0)
                neuer_tile.x = zeilen_kacheln[i].x
                neuer_tile.y = zeilen_kacheln[i].y
                zusammengeführt.append(neuer_tile)
                i += 2
            else:
                tile = zeilen_kacheln[i]
                neuer_tile = Kachel(tile.wert, zeile, 0)
                neuer_tile.x = tile.x
                neuer_tile.y = tile.y
                zusammengeführt.append(neuer_tile)
                i += 1
        for j, tile in enumerate(zusammengeführt):
            tile.target_x = j * RECHTECK_BREITE
            tile.target_y = zeile * RECHTECK_HOEHE
            tile.spalte = j
            tile.zeile = zeile
            neues_gitter[zeile][j] = tile
    neue_kacheln = {}
    for i in range(ZEILEN):
        for j in range(SPALTEN):
            if neues_gitter[i][j] is not None:
                neue_kacheln[f"{i}{j}"] = neues_gitter[i][j]
    return neue_kacheln

def bewege_rechts(kacheln):
    gitter = erstelle_gitter_aus_kacheln(kacheln)
    neues_gitter = [[None for _ in range(SPALTEN)] for _ in range(ZEILEN)]
    for zeile in range(ZEILEN):
        zeilen_kacheln = [tile for tile in gitter[zeile] if tile is not None]
        zusammengeführt = []
        i = len(zeilen_kacheln) - 1
        while i >= 0:
            if i - 1 >= 0 and zeilen_kacheln[i].wert == zeilen_kacheln[i - 1].wert:
                neuer_wert = zeilen_kacheln[i].wert * 2
                neuer_tile = Kachel(neuer_wert, zeile, 0)
                neuer_tile.x = zeilen_kacheln[i].x
                neuer_tile.y = zeilen_kacheln[i].y
                zusammengeführt.append(neuer_tile)
                i -= 2
            else:
                tile = zeilen_kacheln[i]
                neuer_tile = Kachel(tile.wert, zeile, 0)
                neuer_tile.x = tile.x
                neuer_tile.y = tile.y
                zusammengeführt.append(neuer_tile)
                i -= 1
        zusammengeführt.reverse()
        start_spalte = SPALTEN - len(zusammengeführt)
        for idx, tile in enumerate(zusammengeführt):
            spalte = start_spalte + idx
            tile.target_x = spalte * RECHTECK_BREITE
            tile.target_y = zeile * RECHTECK_HOEHE
            tile.spalte = spalte
            tile.zeile = zeile
            neues_gitter[zeile][spalte] = tile
    neue_kacheln = {}
    for i in range(ZEILEN):
        for j in range(SPALTEN):
            if neues_gitter[i][j] is not None:
                neue_kacheln[f"{i}{j}"] = neues_gitter[i][j]
    return neue_kacheln

def bewege_oben(kacheln):
    gitter = erstelle_gitter_aus_kacheln(kacheln)
    neues_gitter = [[None for _ in range(SPALTEN)] for _ in range(ZEILEN)]
    for spalte in range(SPALTEN):
        spalten_kacheln = [gitter[zeile][spalte] for zeile in range(ZEILEN) if gitter[zeile][spalte] is not None]
        zusammengeführt = []
        i = 0
        while i < len(spalten_kacheln):
            if i + 1 < len(spalten_kacheln) and spalten_kacheln[i].wert == spalten_kacheln[i + 1].wert:
                neuer_wert = spalten_kacheln[i].wert * 2
                neuer_tile = Kachel(neuer_wert, 0, spalte)
                neuer_tile.x = spalten_kacheln[i].x
                neuer_tile.y = spalten_kacheln[i].y
                zusammengeführt.append(neuer_tile)
                i += 2
            else:
                tile = spalten_kacheln[i]
                neuer_tile = Kachel(tile.wert, 0, spalte)
                neuer_tile.x = tile.x
                neuer_tile.y = tile.y
                zusammengeführt.append(neuer_tile)
                i += 1
        for i, tile in enumerate(zusammengeführt):
            tile.target_x = spalte * RECHTECK_BREITE
            tile.target_y = i * RECHTECK_HOEHE
            tile.spalte = spalte
            tile.zeile = i
            neues_gitter[i][spalte] = tile
    neue_kacheln = {}
    for i in range(ZEILEN):
        for j in range(SPALTEN):
            if neues_gitter[i][j] is not None:
                neue_kacheln[f"{i}{j}"] = neues_gitter[i][j]
    return neue_kacheln

def bewege_unten(kacheln):
    gitter = erstelle_gitter_aus_kacheln(kacheln)
    neues_gitter = [[None for _ in range(SPALTEN)] for _ in range(ZEILEN)]
    for spalte in range(SPALTEN):
        spalten_kacheln = [gitter[zeile][spalte] for zeile in range(ZEILEN) if gitter[zeile][spalte] is not None]
        zusammengeführt = []
        i = len(spalten_kacheln) - 1
        while i >= 0:
            if i - 1 >= 0 and spalten_kacheln[i].wert == spalten_kacheln[i - 1].wert:
                neuer_wert = spalten_kacheln[i].wert * 2
                neuer_tile = Kachel(neuer_wert, 0, spalte)
                neuer_tile.x = spalten_kacheln[i].x
                neuer_tile.y = spalten_kacheln[i].y
                zusammengeführt.append(neuer_tile)
                i -= 2
            else:
                tile = spalten_kacheln[i]
                neuer_tile = Kachel(tile.wert, 0, spalte)
                neuer_tile.x = tile.x
                neuer_tile.y = tile.y
                zusammengeführt.append(neuer_tile)
                i -= 1
        zusammengeführt.reverse()
        start_zeile = ZEILEN - len(zusammengeführt)
        for idx, tile in enumerate(zusammengeführt):
            zeile = start_zeile + idx
            tile.target_x = spalte * RECHTECK_BREITE
            tile.target_y = zeile * RECHTECK_HOEHE
            tile.spalte = spalte
            tile.zeile = zeile
            neues_gitter[zeile][spalte] = tile
    neue_kacheln = {}
    for i in range(ZEILEN):
        for j in range(SPALTEN):
            if neues_gitter[i][j] is not None:
                neue_kacheln[f"{i}{j}"] = neues_gitter[i][j]
    return neue_kacheln

# -------------------------------
# Animation: Übergang zu den Zielpositionen
# -------------------------------
def animieren_bewegung(oberflaeche, kacheln, dauer=150):
    if not pygame.display.get_surface():
        return
    startpositionen = {tile: (tile.x, tile.y) for tile in kacheln.values()}
    startzeit = pygame.time.get_ticks()
    while True:
        if not pygame.display.get_surface():
            break
        vergangene_zeit = pygame.time.get_ticks() - startzeit
        t = min(1, vergangene_zeit / dauer)
        for tile in kacheln.values():
            start_x, start_y = startpositionen[tile]
            tile.x = start_x + (tile.target_x - start_x) * t
            tile.y = start_y + (tile.target_y - start_y) * t
        zeichnen(oberflaeche, kacheln)
        if t >= 1:
            break
        pygame.time.delay(10)
    for tile in kacheln.values():
        tile.x = tile.target_x
        tile.y = tile.target_y

# -------------------------------
# Durchführung eines Zuges
# -------------------------------
def kacheln_bewegen(oberflaeche, kacheln, richtung):
    if richtung == "links":
        neue_kacheln = bewege_links(kacheln)
    elif richtung == "rechts":
        neue_kacheln = bewege_rechts(kacheln)
    elif richtung == "oben":
        neue_kacheln = bewege_oben(kacheln)
    elif richtung == "unten":
        neue_kacheln = bewege_unten(kacheln)
    else:
        return kacheln

    animieren_bewegung(oberflaeche, neue_kacheln)

    # Ist das Spielfeld voll, gilt es als verloren.
    if len(neue_kacheln) == ZEILEN * SPALTEN:
        return "verloren"

    zeile, spalte = zufaellige_position(neue_kacheln)
    neuer_tile = Kachel(random.choice([2, 4]), zeile, spalte)
    neue_kacheln[f"{zeile}{spalte}"] = neuer_tile
    zeichnen(oberflaeche, neue_kacheln)
    return neue_kacheln

# -------------------------------
# Initiale Kacheln erzeugen
# -------------------------------
def kacheln_generieren():
    kacheln = {}
    for _ in range(2):
        zeile, spalte = zufaellige_position(kacheln)
        kacheln[f"{zeile}{spalte}"] = Kachel(2, zeile, spalte)
    return kacheln

# -------------------------------
# Game-Over-Menü (nur Maussteuerung, mit Hover-Effekt)
# Die Schaltflächen haben einen vertikalen Abstand von 40 Pixeln.
# -------------------------------
def spiel_menue(oberflaeche):
    breite, hoehe = oberflaeche.get_size()
    optionen = ["Erneut spielen", "Beenden"]
    highlight_farbe = (255, 0, 0)
    normale_farbe = SCHRIFT_FARBE

    while True:
        oberflaeche.fill(HINTERGRUND_FARBE)
        titel = SCHRIFT.render("Spiel vorbei", True, SCHRIFT_FARBE)
        oberflaeche.blit(
            titel,
            (breite // 2 - titel.get_width() // 2,
             hoehe // 3 - titel.get_height() // 2)
        )
        optionen_positionen = []
        for i, opt in enumerate(optionen):
            text = SCHRIFT.render(opt, True, normale_farbe)
            x = breite // 2 - text.get_width() // 2
            y = hoehe // 2 + i * 100  # Vertikaler Abstand von 100 Pixeln
            optionen_positionen.append((x, y, text.get_width(), text.get_height()))

        maus_x, maus_y = pygame.mouse.get_pos()
        gehighlightet = -1
        for i, (x, y, w, h) in enumerate(optionen_positionen):
            if x <= maus_x <= x + w and y <= maus_y <= y + h:
                gehighlightet = i
                break

        for i, opt in enumerate(optionen):
            farbe = highlight_farbe if i == gehighlightet else normale_farbe
            text = SCHRIFT.render(opt, True, farbe)
            oberflaeche.blit(text, (optionen_positionen[i][0],
                                     optionen_positionen[i][1]))

        pygame.display.update()

        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                quit()
            if ereignis.type == pygame.MOUSEBUTTONDOWN and gehighlightet != -1:
                return gehighlightet

        pygame.time.delay(10)

# -------------------------------
# Hauptspiel-Schleife
# -------------------------------
def hauptspiel(oberflaeche):
    uhr = pygame.time.Clock()
    laeufig = True
    kacheln = kacheln_generieren()
    zeichnen(oberflaeche, kacheln)
    bewegung_im_Gange = False
    while laeufig:
        uhr.tick(FPS)
        if not pygame.display.get_surface():
            break
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                laeufig = False
                break
            if ereignis.type == pygame.KEYDOWN and not bewegung_im_Gange:
                if ereignis.key == pygame.K_LEFT:
                    bewegung_im_Gange = True
                    ergebnis = kacheln_bewegen(oberflaeche, kacheln, "links")
                elif ereignis.key == pygame.K_RIGHT:
                    bewegung_im_Gange = True
                    ergebnis = kacheln_bewegen(oberflaeche, kacheln, "rechts")
                elif ereignis.key == pygame.K_UP:
                    bewegung_im_Gange = True
                    ergebnis = kacheln_bewegen(oberflaeche, kacheln, "oben")
                elif ereignis.key == pygame.K_DOWN:
                    bewegung_im_Gange = True
                    ergebnis = kacheln_bewegen(oberflaeche, kacheln, "unten")
                else:
                    continue
                pygame.event.clear()
                bewegung_im_Gange = False
                if ergebnis == "verloren":
                    auswahl = spiel_menue(oberflaeche)
                    if auswahl == 0:  # "Erneut spielen"
                        hauptspiel(oberflaeche)
                    elif auswahl == 1:  # "Beenden"
                        laeufig = False
                else:
                    kacheln = ergebnis
        zeichnen(oberflaeche, kacheln)
    pygame.quit()

if __name__ == "__main__":
    hauptspiel(FENSTER)
