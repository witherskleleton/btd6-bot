import os, keyboard, psutil, sys
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk

"""
process_name = "BloonsTD6.exe"

def check_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

if check_process_running(process_name):
        pass
else:
        messagebox.showerror("PROCESS NOT FOUND", "bloonstd6.exe was not found")
        sys.exit()
"""

# Function to get the list of script files in a directory
def get_script_list(directory):
    script_list = []
    for filename in os.listdir(directory):
        script_list.append(filename)
    return script_list

# Directory containing the scripts
script_directory = r"btd6botv1\scripts"

# Get the list of scripts
script_options = get_script_list(script_directory)

# Function to validate the hotkey entry
def validate_hotkey(char):
    if len(char) == 1 and char.isalnum():
        return True
    return False


def runscript():
    selected_script = select.get()
    if selected_script:
        script_path = os.path.join(script_directory, selected_script)
        try:
            subprocess.run(['python', script_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to run script: {e}")
    else:
        messagebox.showwarning("No Script Selected", "Please select a script to run.")

    def run_infinite():
        while checkbox_var.get():  # Run as long as the checkbox is checked
            subprocess.run(['python', script_path])  # Replace 'python' with your interpreter if needed

        # Start running the script infinitely when checkbox is checked

    if checkbox_var.get():
        run_infinite()
def mainapp():
    selected_item = select.get()
    hotkey = entry.get()
    keyboard.add_hotkey(hotkey=hotkey,callback=runscript)

def stop():
    # Function to close the Tkinter window
    sys.exit()
    root.destroy()
    # Function to terminate another process
    process_name = "BloonsTD6.exe"

    # Find and terminate the process
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            break  # Terminate only the first matching process found

def checkbox_changed():
    if checkbox_var.get():
        runscript()

root = Tk()

root.geometry("300x400")
root.title("BTD6 BOT")

icon = PhotoImage(file="btd6botpic.png")
root.iconphoto(True,icon)
root.config(background="#111810")

options = Label(root,
                text="Select a script:",
                fg='#0080FE',
                bg='#111810',
                )
options.pack(pady=10)

select = ttk.Combobox(root,
                 values=script_options,
                 state="readonly",
                 foreground='#0080FE',
                 background='#111810'
                 )
select.pack(pady=10)

hotkeyexplain = Label(root,
                      text="Select hotkey (RESART PROGRAM TO DELETE):",
                      fg='#0080FE',
                      bg='#111810',
                      )
hotkeyexplain.pack(pady=10)

validate_cmd = root.register(validate_hotkey)
entry = Entry(root,
                  fg='#111810',
                  bg='#0080FE',
                  validate="key",
                  validatecommand=(validate_cmd, '%P'),
                  )
entry.pack(pady=10)

confirm = Button(root,
                text="Confirm",
                command=mainapp,
                fg='#0080FE',
                bg='#111810',
                )
confirm.pack(pady=10)

# Create a checkbox variable
checkbox_var = tk.BooleanVar()

# Function to handle checkbox state change


# Create a checkbox
checkbox = Checkbutton(root,
                        text="Run Script Infinitely",
                        fg='#0080FE',
                        bg='#111810',
                        activeforeground='#0080FE',
                        activebackground='#111810',
                        variable=checkbox_var,
                        command=checkbox_changed,
                     )
checkbox.pack(pady=20)

emergencystop = Button(root,
                           text="STOP",
                           command=stop,
                           fg="white",
                           bg="red",
                           activeforeground="white",
                           activebackground="red",
                           )
emergencystop.pack(pady=10)
root.mainloop()
