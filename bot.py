# python
import os
import sys
import threading
import time
import subprocess
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

SCRIPT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "btd6botv1", "scripts"))

def get_script_list(directory):
    if not os.path.isdir(directory):
        return []
    return sorted([f for f in os.listdir(directory) if f.endswith(".py")])

script_options = get_script_list(SCRIPT_DIR)

def validate_hotkey(char):
    # einfache Prüfung: nicht leer (keyboard lib erfordert evtl. root auf Linux)
    return len(char.strip()) > 0

def run_script_once(script_path):
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Script fehlgeschlagen: {e}")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

def run_script_loop(script_path, stop_event):
    while not stop_event.is_set():
        try:
            proc = subprocess.Popen([sys.executable, script_path])
            # Warte auf Ende oder Stop
            while proc.poll() is None:
                if stop_event.is_set():
                    proc.terminate()
                    break
                time.sleep(0.2)
        except Exception as e:
            messagebox.showerror("Fehler", f"Loop-Fehler: {e}")
            break
        # kurze Pause zwischen Durchläufen
        time.sleep(0.5)

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x400")
        self.root.title("BTD6 BOT")
        self.root.config(background="#111810")

        ttk.Label(root, text="Select a script:", foreground='#0080FE', background='#111810').pack(pady=10)
        self.select = ttk.Combobox(root, values=script_options, state="readonly")
        self.select.pack(pady=10)

        ttk.Label(root, text="Select hotkey (RESTART PROGRAM TO DELETE):", foreground='#0080FE', background='#111810').pack(pady=10)

        vcmd = (root.register(validate_hotkey), '%P')
        self.entry = tk.Entry(root, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10)

        tk.Button(root, text="Confirm", command=self.confirm).pack(pady=10)

        self.checkbox_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Run Script Infinitely", variable=self.checkbox_var, command=self.checkbox_changed).pack(pady=20)

        tk.Button(root, text="STOP", fg="white", bg="red", command=self.stop).pack(pady=10)

        self.loop_thread = None
        self.loop_stop_event = threading.Event()

    def confirm(self):
        self.hotkey = self.entry.get().strip()
        self.selected_script = self.select.get()
        if not self.selected_script:
            messagebox.showwarning("Keine Auswahl", "Bitte ein Script wählen.")
            return
        if not validate_hotkey(self.hotkey):
            messagebox.showwarning("Hotkey ungültig", "Bitte gültigen Hotkey eingeben.")
            return
        # Hinweis: keyboard.register kann Root-Rechte benötigen; hier nur speichern
        messagebox.showinfo("Bestätigt", f"Hotkey: {self.hotkey} für {self.selected_script}")

    def _start_script_thread(self, repeat=False):
        script_path = os.path.join(SCRIPT_DIR, self.select.get())
        if not os.path.isfile(script_path):
            messagebox.showerror("Fehler", "Script nicht gefunden.")
            return
        if repeat:
            if self.loop_thread and self.loop_thread.is_alive():
                return
            self.loop_stop_event.clear()
            self.loop_thread = threading.Thread(target=run_script_loop, args=(script_path, self.loop_stop_event), daemon=True)
            self.loop_thread.start()
        else:
            threading.Thread(target=run_script_once, args=(script_path,), daemon=True).start()

    def checkbox_changed(self):
        if self.checkbox_var.get():
            self._start_script_thread(repeat=True)
        else:
            self.loop_stop_event.set()

    def stop(self):
        # Stoppe lokale Threads
        self.loop_stop_event.set()
        # Versuche externen Prozess zu terminieren
        target = "BloonsTD6.exe"
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info.get('name') == target:
                    proc.terminate()
                    break
            except Exception:
                pass
        # Schließe GUI
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
