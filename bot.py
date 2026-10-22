# python
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from scripts.coordinates import (
    COORDINATE_LABELS,
    DEFAULT_COORDINATES,
    load_coordinates,
    save_coordinates,
)

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
SCRIPT_OPTIONS = sorted(
    name for name in os.listdir(SCRIPT_DIR)
    if name.endswith(".py") and name != "coordinates.py"
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("BTD6 Bot")
        self.root.geometry("440x500")
        self.root.minsize(400, 420)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.coordinates = load_coordinates()
        self.capture_events = queue.Queue()
        self.capture_listener = None
        self.capture_mouse = None
        self.active_coordinate = None
        self.loop_stop_event = threading.Event()
        self.process = None
        self.loop_thread = None
        self.process_lock = threading.Lock()

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Script").pack(anchor="w")
        self.script_select = ttk.Combobox(frame, values=SCRIPT_OPTIONS, state="readonly")
        self.script_select.pack(fill="x", pady=(4, 14))
        if SCRIPT_OPTIONS:
            self.script_select.current(0)

        ttk.Separator(frame).pack(fill="x", pady=(0, 12))
        ttk.Label(frame, text="Save a screen location").pack(anchor="w")
        ttk.Label(
            frame,
            text="Choose a step, click Capture, move the cursor, then press Ctrl+K.",
            wraplength=390,
        ).pack(anchor="w", pady=(4, 8))

        self.coordinate_select = ttk.Combobox(
            frame,
            values=[
                "{} - {}".format(name, COORDINATE_LABELS[name])
                for name in DEFAULT_COORDINATES
            ],
            state="readonly",
        )
        self.coordinate_select.pack(fill="x")
        self.coordinate_select.current(0)
        self.coordinate_value = ttk.Label(frame, text="")
        self.coordinate_value.pack(anchor="w", pady=4)

        capture_buttons = ttk.Frame(frame)
        capture_buttons.pack(fill="x", pady=(4, 6))
        ttk.Button(capture_buttons, text="Capture location", command=self.begin_capture).pack(
            side="left"
        )
        ttk.Button(capture_buttons, text="Cancel capture", command=self.cancel_capture).pack(
            side="left", padx=8
        )
        self.status = ttk.Label(frame, text="Ready")
        self.status.pack(anchor="w", pady=(0, 12))
        self.coordinate_select.bind("<<ComboboxSelected>>", self.update_coordinate_label)
        self.update_coordinate_label()

        ttk.Separator(frame).pack(fill="x", pady=(0, 12))
        ttk.Label(frame, text="Run").pack(anchor="w")
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(8, 0))
        ttk.Button(controls, text="Run once", command=self.run_once).pack(side="left")
        self.repeat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls,
            text="Repeat until stopped",
            variable=self.repeat_var,
            command=self.toggle_repeat,
        ).pack(side="left", padx=12)
        ttk.Button(frame, text="Stop", command=self.stop_scripts).pack(anchor="w", pady=12)

        self.poll_capture_events()

    def update_coordinate_label(self, _event=None):
        name = self.selected_coordinate_name()
        self.coordinate_value.config(text="Current: {}".format(self.coordinates[name]))

    def selected_coordinate_name(self):
        return self.coordinate_select.get().split(" - ", 1)[0]

    def begin_capture(self):
        self.cancel_capture()
        while True:
            try:
                self.capture_events.get_nowait()
            except queue.Empty:
                break
        name = self.selected_coordinate_name()
        try:
            from pynput import keyboard, mouse

            self.capture_mouse = mouse.Controller()
            self.active_coordinate = name
            self.capture_listener = keyboard.GlobalHotKeys(
                {"<ctrl>+k": lambda: self.capture_events.put(self.capture_mouse.position)}
            )
            self.capture_listener.start()
        except Exception as error:
            self.cancel_capture()
            messagebox.showerror(
                "Capture unavailable",
                "Could not start the global Ctrl+K listener: {}".format(error),
            )
            return
        self.status.config(text="Move the cursor to {!r}, then press Ctrl+K.".format(name))

    def cancel_capture(self):
        if self.capture_listener is not None:
            self.capture_listener.stop()
            self.capture_listener = None
        self.active_coordinate = None
        if hasattr(self, "status"):
            self.status.config(text="Ready")

    def poll_capture_events(self):
        try:
            position = self.capture_events.get_nowait()
        except queue.Empty:
            pass
        else:
            if self.active_coordinate is not None:
                name = self.active_coordinate
                self.coordinates[name] = tuple(position)
                try:
                    save_coordinates(self.coordinates)
                except OSError as error:
                    messagebox.showerror("Could not save settings", str(error))
                else:
                    self.update_coordinate_label()
                    self.cancel_capture()
                    self.status.config(text="Saved {} at {}.".format(name, position))
                if self.active_coordinate is not None:
                    self.cancel_capture()
        self.root.after(100, self.poll_capture_events)

    def selected_script_path(self):
        name = self.script_select.get()
        if name not in SCRIPT_OPTIONS:
            messagebox.showwarning("No script selected", "Choose a script first.")
            return None
        return os.path.join(SCRIPT_DIR, name)

    def run_once(self):
        script_path = self.selected_script_path()
        if script_path is not None:
            self.loop_stop_event.clear()
            threading.Thread(target=self.run_process, args=(script_path,), daemon=True).start()

    def run_process(self, script_path):
        with self.process_lock:
            if self.process is not None and self.process.poll() is None:
                return
            try:
                process = subprocess.Popen([sys.executable, script_path])
            except OSError as error:
                self.root.after(
                    0, lambda error=error: messagebox.showerror("Could not run script", str(error))
                )
                return
            self.process = process
        try:
            return_code = process.wait()
            if return_code and not self.loop_stop_event.is_set():
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Script failed", "{} exited with code {}.".format(
                            os.path.basename(script_path), return_code
                        )
                    ),
                )
        finally:
            with self.process_lock:
                if self.process is process:
                    self.process = None

    def toggle_repeat(self):
        if self.repeat_var.get():
            script_path = self.selected_script_path()
            if script_path is None:
                self.repeat_var.set(False)
                return
            self.loop_stop_event.clear()
            self.loop_thread = threading.Thread(
                target=self.run_loop, args=(script_path,), daemon=True
            )
            self.loop_thread.start()
        else:
            self.loop_stop_event.set()

    def run_loop(self, script_path):
        while not self.loop_stop_event.is_set():
            self.run_process(script_path)
            self.loop_stop_event.wait(0.5)

    def stop_scripts(self):
        self.loop_stop_event.set()
        with self.process_lock:
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()
        self.repeat_var.set(False)

    def close(self):
        self.cancel_capture()
        self.stop_scripts()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
