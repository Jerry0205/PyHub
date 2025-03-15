import os
import sys

def resource_path(relative_path):
    """Ermittelt den korrekten Pfad für Ressourcen, funktioniert sowohl in der 
    normalen Python-Umgebung als auch in der kompilierten EXE"""
    try:
        # PyInstaller erstellt einen temporären Ordner und speichert den Pfad in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
