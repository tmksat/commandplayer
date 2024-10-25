#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, simpledialog
import subprocess
import json


class CommandPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Command Player")

        self.load_commands_from_file()

        self.create_widgets()
        self.configure_layout()

    def create_widgets(self):
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.create_command_buttons()

        self.response_area = tk.Text(self.master, height=10, width=50)
        self.response_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.control_frame = ttk.Frame(self.master)
        self.control_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.clear_btn = ttk.Button(
            self.control_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.add_btn = ttk.Button(
            self.control_frame, text="Add Button", command=self.add_button)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.remove_btn = ttk.Button(
            self.control_frame, text="Remove Button", command=self.remove_button)
        self.remove_btn.pack(side=tk.LEFT, padx=5)

        self.exit_btn = ttk.Button(
            self.control_frame, text="Exit", command=self.master.quit)
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

    def configure_layout(self):
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def create_command_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for i, command in enumerate(self.commands):
            btn = ttk.Button(
                self.button_frame, text=command['name'], command=lambda x=i: self.execute_command(x))
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

            edit_btn = ttk.Button(
                self.button_frame, text="Edit", command=lambda x=i: self.edit_command(x))
            edit_btn.grid(row=i, column=1, padx=5, pady=5)

    def execute_command(self, index):
        command = self.commands[index]['command']
        try:
            result = subprocess.check_output(
                command, shell=True, text=True, stderr=subprocess.STDOUT)
            self.response_area.delete(1.0, tk.END)
            self.response_area.insert(tk.END, result)
        except subprocess.CalledProcessError as e:
            self.response_area.delete(1.0, tk.END)
            self.response_area.insert(tk.END, f"Error: {e.output}")

    def edit_command(self, index):
        edit_window = tk.Toplevel(self.master)
        edit_window.title(f"Edit Command {index+1}")

        name_label = ttk.Label(edit_window, text="Button Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(edit_window, width=50)
        name_entry.insert(0, self.commands[index]['name'])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        command_label = ttk.Label(edit_window, text="Command:")
        command_label.grid(row=1, column=0, padx=5, pady=5)
        command_entry = ttk.Entry(edit_window, width=50)
        command_entry.insert(0, self.commands[index]['command'])
        command_entry.grid(row=1, column=1, padx=5, pady=5)

        save_btn = ttk.Button(edit_window, text="Save", command=lambda: self.save_command(
            index, name_entry.get(), command_entry.get(), edit_window))
        save_btn.grid(row=2, column=1, pady=5)

    def save_command(self, index, new_name, new_command, window):
        self.commands[index] = {'name': new_name, 'command': new_command}
        self.save_commands_to_file()
        self.create_command_buttons()
        window.destroy()

    def save_commands_to_file(self, filename='commands.json'):
        with open(filename, 'w') as f:
            json.dump(self.commands, f)

    def load_commands_from_file(self, filename='commands.json'):
        try:
            with open(filename, 'r') as f:
                self.commands = json.load(f)
        except FileNotFoundError:
            self.commands = [{'name': f'Command {i+1}', 'command': cmd}
                             for i, cmd in enumerate(["ls", "pwd", "date", "whoami", "uname -a"])]

    def clear_output(self):
        self.response_area.delete(1.0, tk.END)

    def add_button(self):
        new_name = simpledialog.askstring("Add Button", "Enter button name:")
        if new_name:
            self.commands.append({'name': new_name, 'command': ''})
            self.save_commands_to_file()
            self.create_command_buttons()

    def remove_button(self):
        if len(self.commands) > 1:
            self.commands.pop()
            self.save_commands_to_file()
            self.create_command_buttons()
        else:
            tk.messagebox.showwarning(
                "Warning", "Cannot remove the last button.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandPlayer(root)
    root.mainloop()
