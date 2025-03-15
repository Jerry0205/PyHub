#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PYHUB - Spielesammlung
"""

import sys
import os

# Stelle sicher, dass das aktuelle Verzeichnis im Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importiere und starte das Hauptmenü
from main_menu import GameLauncher

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
