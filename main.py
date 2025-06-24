#!/usr/bin/env python3
"""
Programme modulaire d'enregistrement audio avec détection automatique de silence
Auteur: Julien Balderiotti
Version: 1.0
"""
from tkinter import messagebox
from recorder_app import AudioRecorderGUI


if __name__ == "__main__":
    # Vérifier les dépendances
    try:
        import pyaudio
        import numpy as np
        print("✅ Toutes les dépendances sont installées")
        
        try:
            app = AudioRecorderGUI()
            app.run()
        except Exception as e:
            print(f"Erreur lors du lancement de l'application: {e}")
            messagebox.showerror("Erreur", f"Impossible de lancer l'application:\n{e}")

    except ImportError as e:
        print("❌ Dépendances manquantes:")
        print("Installez les avec: pip install pyaudio numpy")
        print(f"Erreur: {e}")