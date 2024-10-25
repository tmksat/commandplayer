#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import subprocess
import json
import threading
import queue
import signal
import os
import pty
import select
import time


class CommandPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Command Player")

        self.load_commands_from_file()

        self.create_widgets()
        self.configure_layout()

        self.processes = {}
        self.threads = {}
        self.queues = {}
        self.output_buffer = []  # 出力をバッファリングするリスト

    def create_widgets(self):
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.create_command_buttons()

        self.response_area = tk.Text(self.master, height=10, width=50)
        self.response_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.scrollbar = ttk.Scrollbar(
            self.master, orient="vertical", command=self.response_area.yview)
        self.response_area['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.grid(row=0, column=2, sticky='ns')

        self.control_frame = ttk.Frame(self.master)
        self.control_frame.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

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
            self.control_frame, text="Exit", command=self.on_exit)
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

    def configure_layout(self):
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def create_command_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for i, command in enumerate(self.commands):
            btn_frame = ttk.Frame(self.button_frame)
            btn_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

            btn = ttk.Button(
                btn_frame, text=command['name'], command=lambda x=i: self.execute_command(x))
            btn.pack(side=tk.LEFT, padx=(0, 5))

            kill_btn = ttk.Button(btn_frame, text="Kill",
                                  command=lambda x=i: self.kill_command(x))
            kill_btn.pack(side=tk.LEFT)

            edit_btn = ttk.Button(btn_frame, text="Edit",
                                  command=lambda x=i: self.edit_command(x))
            edit_btn.pack(side=tk.LEFT, padx=(5, 0))

    def execute_command(self, index):
        if index in self.processes:
            if self.processes[index].poll() is None:
                self.output_buffer.append(
                    "\nTerminating the existing process...\n")
                self.kill_command(index)
            else:
                del self.processes[index]
                del self.queues[index]
                del self.threads[index]

        self.output_buffer.append(
            f"\nExecuting command: {self.commands[index]['command']}\n")

        master_fd, slave_fd = pty.openpty()

        process = subprocess.Popen(self.commands[index]['command'], shell=True,
                                   stdout=slave_fd, stderr=slave_fd, stdin=slave_fd, preexec_fn=os.setsid)
        self.processes[index] = process

        os.close(slave_fd)

        q = queue.Queue()
        self.queues[index] = q

        thread = threading.Thread(
            target=self.read_output, args=(master_fd, q, index))
        thread.daemon = True
        thread.start()
        self.threads[index] = thread

        self.update_output(index)

    def read_output(self, fd, q, index):
        while True:
            try:
                rlist, _, _ = select.select([fd], [], [], 0.1)
                if rlist:
                    output = os.read(fd, 1024).decode(errors='replace')
                    if output:
                        q.put(output)
                    else:
                        break
                if index not in self.processes:
                    break
            except (OSError, ValueError):
                break
        os.close(fd)
        q.put(None)  # シグナルとして None を送信

    def update_output(self, index):
        if index not in self.queues:
            return

        try:
            while True:
                data = self.queues[index].get_nowait()
                if data is None:  # プロセスが終了したことを示す
                    self.output_buffer.append("\nProcess finished\n")
                    break
                self.output_buffer.append(data)
        except queue.Empty:
            pass

        # 一定間隔（500ミリ秒）でテキストエリアを更新
        if self.output_buffer:
            self.response_area.insert(tk.END, ''.join(self.output_buffer))
            self.response_area.see(tk.END)
            self.output_buffer.clear()

        # 次の更新をスケジュール
        self.master.after(500, lambda: self.update_output(index))

    def kill_command(self, index):
        if index in self.processes:
            try:
                os.killpg(os.getpgid(
                    self.processes[index].pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            del self.processes[index]
            self.output_buffer.append("\nProcess terminated\n")

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
            messagebox.showwarning("Warning", "Cannot remove the last button.")

    def on_exit(self):
        for index in list(self.processes.keys()):
            self.kill_command(index)
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandPlayer(root)
    root.mainloop()
