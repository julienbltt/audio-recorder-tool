import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import os
import time
from datetime import datetime

from recorder import AudioRecorder


class AudioRecorderGUI:
    """Interface graphique sécurisée pour l'enregistreur audio"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enregistreur Audio - Détection Automatique (Version Sécurisée)")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Thème moderne
        self.root.configure(bg='#f0f0f0')
        
        # Variables d'état
        self.is_recording = False
        self.last_filename = None
        self.start_time = None
        
        # Enregistreur avec callbacks sécurisés
        self.recorder = AudioRecorder()
        self.recorder.on_recording_start = self.on_recording_start
        self.recorder.on_recording_stop = self.on_recording_stop
        self.recorder.on_volume_update = self.on_volume_update
        
        self.setup_ui()
        self.setup_microphones()
        
        # Fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre
        title_label = tk.Label(
            self.root, 
            text="🎤 Enregistreur Audio Intelligent",
            font=("Arial", 18, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=20)
        
        # Sélection du microphone
        mic_frame = tk.Frame(self.root, bg='#f0f0f0')
        mic_frame.pack(pady=10)
        
        tk.Label(mic_frame, text="Microphone:", font=("Arial", 10), bg='#f0f0f0').pack(side=tk.LEFT)
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(mic_frame, textvariable=self.mic_var, width=40, state='readonly')
        self.mic_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.mic_combo.bind('<<ComboboxSelected>>', self.on_mic_selected)
        
        # Paramètres de silence
        settings_frame = tk.LabelFrame(self.root, text="Paramètres de détection", bg='#f0f0f0', font=("Arial", 10))
        settings_frame.pack(pady=15, padx=20, fill=tk.X)
        
        # Seuil de silence
        threshold_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        threshold_frame.pack(fill=tk.X, pady=5)
        tk.Label(threshold_frame, text="Seuil de silence:", bg='#f0f0f0').pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=1000)
        threshold_scale = tk.Scale(
            threshold_frame, 
            from_=100, to=5000, 
            orient=tk.HORIZONTAL, 
            variable=self.threshold_var,
            bg='#f0f0f0'
        )
        threshold_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        threshold_scale.bind("<Motion>", self.on_settings_change)
        
        # Durée de silence
        duration_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        duration_frame.pack(fill=tk.X, pady=5)
        tk.Label(duration_frame, text="Durée de silence (s):", bg='#f0f0f0').pack(side=tk.LEFT)
        self.duration_var = tk.DoubleVar(value=2.0)
        duration_scale = tk.Scale(
            duration_frame, 
            from_=0.5, to=5.0, 
            resolution=0.1,
            orient=tk.HORIZONTAL, 
            variable=self.duration_var,
            bg='#f0f0f0'
        )
        duration_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        duration_scale.bind("<Motion>", self.on_settings_change)
        
        # Indicateur de volume
        volume_frame = tk.Frame(self.root, bg='#f0f0f0')
        volume_frame.pack(pady=10)
        
        tk.Label(volume_frame, text="Volume:", font=("Arial", 10), bg='#f0f0f0').pack()
        self.volume_progress = ttk.Progressbar(
            volume_frame, 
            mode='determinate', 
            length=300,
            style='Volume.Horizontal.TProgressbar'
        )
        self.volume_progress.pack(pady=5)
        
        # État de l'enregistrement
        self.status_label = tk.Label(
            self.root,
            text="Prêt à enregistrer",
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=10)
        
        # Bouton principal
        self.record_button = tk.Button(
            self.root,
            text="🔴 Commencer l'enregistrement",
            font=("Arial", 14, "bold"),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            command=self.toggle_recording,
            relief=tk.RAISED,
            borderwidth=2
        )
        self.record_button.pack(pady=20)
        
        # Bouton de sauvegarde
        self.save_button = tk.Button(
            self.root,
            text="💾 Sauvegarder",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white',
            padx=15,
            pady=5,
            command=self.save_recording,
            state=tk.DISABLED
        )
        self.save_button.pack(pady=5)
        
        # Timer
        self.timer_label = tk.Label(
            self.root,
            text="00:00",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        self.timer_label.pack(pady=5)
        
        # Configurer le style de la progress bar
        style = ttk.Style()
        style.configure('Volume.Horizontal.TProgressbar', background='#4CAF50')
    
    def setup_microphones(self):
        """Configure la liste des microphones"""
        try:
            microphones = self.recorder.mic_selector.get_microphones()
            if not microphones:
                messagebox.showwarning("Attention", "Aucun microphone détecté!")
                return
            
            mic_names = [f"{mic['name']} (Index: {mic['index']})" for mic in microphones]
            
            self.mic_combo['values'] = mic_names
            self.mic_combo.current(0)
            self.recorder.set_microphone(microphones[0]['index'])
            print(f"Microphone par défaut sélectionné: {microphones[0]['name']}")
        except Exception as e:
            print(f"Erreur lors de la configuration des microphones: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la détection des microphones:\n{e}")
    
    def on_mic_selected(self, event):
        """Callback pour la sélection du microphone"""
        try:
            selection = self.mic_combo.current()
            if selection >= 0:
                microphones = self.recorder.mic_selector.get_microphones()
                if selection < len(microphones):
                    self.recorder.set_microphone(microphones[selection]['index'])
                    print(f"Microphone sélectionné: {microphones[selection]['name']}")
        except Exception as e:
            print(f"Erreur lors de la sélection du microphone: {e}")
    
    def on_settings_change(self, event):
        """Callback pour le changement des paramètres"""
        try:
            self.recorder.set_silence_settings(
                self.threshold_var.get(),
                self.duration_var.get()
            )
        except Exception as e:
            print(f"Erreur lors du changement des paramètres: {e}")
    
    def toggle_recording(self):
        """Bascule entre démarrer et arrêter l'enregistrement avec protection"""
        try:
            if not self.is_recording:
                print("🚀 Démarrage de l'enregistrement...")
                self.start_recording()
            else:
                print("🛑 Arrêt manuel demandé...")
                self.stop_recording()
        except Exception as e:
            print(f"Erreur lors du basculement d'enregistrement: {e}")
            messagebox.showerror("Erreur", f"Erreur d'enregistrement:\n{e}")
            # Forcer l'état d'arrêt en cas d'erreur
            self.force_stop_state()
    
    def start_recording(self):
        """Démarre l'enregistrement avec gestion d'erreurs"""
        try:
            if self.recorder.start_recording():
                self.is_recording = True
                self.start_time = time.time()
                # Réinitialiser le timer
                self.timer_label.config(text="00:00")
                self.update_timer()
                print("✅ Enregistrement démarré avec succès")
            else:
                messagebox.showerror("Erreur", "Impossible de démarrer l'enregistrement. Vérifiez votre microphone.")
        except Exception as e:
            print(f"Erreur lors du démarrage: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du démarrage de l'enregistrement:\n{e}")
    
    def stop_recording(self):
        """Arrête l'enregistrement avec gestion d'erreurs"""
        try:
            print("🛑 Arrêt de l'enregistrement...")
            self.recorder.stop_recording()
            self.is_recording = False
            print("✅ Enregistrement arrêté avec succès")
        except Exception as e:
            print(f"Erreur lors de l'arrêt: {e}")
            # Forcer l'état d'arrêt même en cas d'erreur
            self.is_recording = False
            self.force_stop_state()
    
    def force_stop_state(self):
        """Force l'interface en état d'arrêt en cas d'erreur"""
        try:
            self.is_recording = False
            self.record_button.config(
                text="🔴 Commencer l'enregistrement",
                bg='#4CAF50'
            )
            self.status_label.config(
                text="❌ Erreur d'enregistrement - Réessayez",
                fg='#f44336'
            )
            self.volume_progress['value'] = 0
        except Exception as e:
            print(f"Erreur lors de la remise en état: {e}")
    
    def on_recording_start(self):
        """Callback appelé quand l'enregistrement commence (thread-safe)"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
            
            def update_ui():
                try:
                    self.record_button.config(
                        text="⏹️ Arrêter l'enregistrement",
                        bg='#f44336'
                    )
                    self.status_label.config(
                        text="🔴 Enregistrement en cours... Parlez maintenant!",
                        fg='#f44336'
                    )
                    self.save_button.config(state=tk.DISABLED)
                    self.volume_progress['value'] = 0
                except Exception as e:
                    print(f"Erreur dans update_ui (start): {e}")
            
            # Exécuter dans le thread principal
            self.root.after_idle(update_ui)
            
        except Exception as e:
            print(f"Erreur dans on_recording_start: {e}")
    
    def on_recording_stop(self):
        """Callback appelé quand l'enregistrement s'arrête (thread-safe)"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
            
            def update_ui():
                try:
                    self.is_recording = False  # S'assurer que l'état est mis à jour
                    
                    self.record_button.config(
                        text="🔴 Commencer l'enregistrement",
                        bg='#4CAF50'
                    )
                    
                    duration = self.recorder.get_recording_duration()
                    self.status_label.config(
                        text=f"✅ Enregistrement terminé ({duration:.1f}s)",
                        fg='#4CAF50'
                    )
                    self.save_button.config(state=tk.NORMAL)
                    self.volume_progress['value'] = 0
                    
                    # Mettre à jour le timer avec la durée finale
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                except Exception as e:
                    print(f"Erreur dans update_ui (stop): {e}")
            
            # Exécuter dans le thread principal
            self.root.after_idle(update_ui)
            
        except Exception as e:
            print(f"Erreur dans on_recording_stop: {e}")
    
    def on_volume_update(self, volume):
        """Callback pour mettre à jour l'indicateur de volume (thread-safe)"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
            
            def update_volume():
                try:
                    # Normaliser le volume pour la progress bar (0-100) avec protection
                    if volume is not None and not np.isnan(volume) and not np.isinf(volume):
                        normalized_volume = min(100, max(0, (volume / 3000) * 100))
                        self.volume_progress['value'] = normalized_volume
                    else:
                        self.volume_progress['value'] = 0
                except Exception as e:
                    print(f"Erreur dans update_volume: {e}")
                    self.volume_progress['value'] = 0
            
            # Exécuter dans le thread principal avec priorité basse
            self.root.after_idle(update_volume)
            
        except Exception as e:
            print(f"Erreur dans on_volume_update: {e}")
    
    def update_timer(self):
        """Met à jour le timer d'enregistrement de manière sécurisée"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
            
            if self.is_recording and self.start_time:
                elapsed = time.time() - self.start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                self.root.after(1000, self.update_timer)
            elif not self.is_recording and hasattr(self.recorder, 'audio_data') and self.recorder.audio_data:
                # Afficher la durée finale de l'enregistrement
                duration = self.recorder.get_recording_duration()
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            else:
                # Reset du timer si pas d'enregistrement
                self.timer_label.config(text="00:00")
        except Exception as e:
            print(f"Erreur dans update_timer: {e}")
            try:
                self.timer_label.config(text="00:00")
            except:
                pass
    
    def save_recording(self):
        """Sauvegarde l'enregistrement avec gestion d'erreurs complète"""
        try:
            if not self.recorder.audio_data:
                messagebox.showwarning("Avertissement", "Aucun enregistrement à sauvegarder!")
                return
            
            # Générer un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"enregistrement_{timestamp}.wav"
            
            # Boîte de dialogue de sauvegarde
            filename = filedialog.asksaveasfilename(
                title="Sauvegarder l'enregistrement",
                defaultextension=".wav",
                filetypes=[("Fichiers WAV", "*.wav"), ("Tous les fichiers", "*.*")],
                initialfile=default_filename
            )
            
            if filename:
                if self.recorder.save_recording(filename):
                    self.last_filename = filename
                    messagebox.showinfo("Succès", f"Enregistrement sauvegardé:\n{filename}")
                    self.status_label.config(
                        text=f"💾 Sauvegardé: {os.path.basename(filename)}",
                        fg='#4CAF50'
                    )
                    print(f"✅ Fichier sauvegardé: {filename}")
                else:
                    messagebox.showerror("Erreur", "Impossible de sauvegarder l'enregistrement!")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
    
    def on_closing(self):
        """Callback pour la fermeture sécurisée de l'application"""
        try:
            if self.is_recording:
                if messagebox.askokcancel("Fermeture", "Un enregistrement est en cours. Voulez-vous vraiment quitter?"):
                    print("🚪 Fermeture forcée - Arrêt de l'enregistrement...")
                    self.is_recording = False
                    self.recorder.cleanup()
                    self.root.destroy()
                else:
                    return  # Annuler la fermeture
            else:
                print("🚪 Fermeture normale de l'application...")
                self.recorder.cleanup()
                self.root.destroy()
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
            # Forcer la fermeture même en cas d'erreur
            try:
                self.recorder.cleanup()
            except:
                pass
            try:
                self.root.destroy()
            except:
                pass
    
    def run(self):
        """Lance l'application"""
        try:
            print("🚀 Démarrage de l'interface graphique...")
            self.root.mainloop()
        except Exception as e:
            print(f"Erreur lors de l'exécution de l'interface: {e}")
            messagebox.showerror("Erreur Fatale", f"Erreur lors de l'exécution:\n{e}")