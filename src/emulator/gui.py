"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from emulator.result import with_newline
from emulator.shell import Shell

WINDOW_SIZE = "820x480"
FONT = "TkFixedFont"
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"


def window_title(shell: Shell) -> str:
    """Собрать заголовок окна из реальных данных ОС."""
    return f"Эмулятор - [{shell.user}@{shell.host}]"


class App:
    """Окно эмулятора: область вывода, приглашение и строка ввода."""

    def __init__(self, shell: Shell):
        """Создать окно для оболочки shell."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(window_title(shell))
        self.root.geometry(WINDOW_SIZE)
        self._build_widgets()

    def _build_widgets(self):
        """Создать область вывода, метку приглашения и поле ввода."""
        self.output = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word", font=FONT,
            background=BACKGROUND, foreground=FOREGROUND,
        )
        self.output.pack(fill="both", expand=True)
        row = tk.Frame(self.root, background=BACKGROUND)
        row.pack(fill="x")
        self.prompt_var = tk.StringVar()
        tk.Label(
            row, textvariable=self.prompt_var, font=FONT,
            background=BACKGROUND, foreground=FOREGROUND,
        ).pack(side="left")
        self.entry = tk.Entry(
            row, font=FONT, background=BACKGROUND, foreground=FOREGROUND,
            insertbackground=FOREGROUND, relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()
        self._refresh_prompt()

    def _refresh_prompt(self):
        """Обновить текст приглашения рядом с полем ввода."""
        self.prompt_var.set(self.shell.prompt())

    def _on_enter(self, _event):
        """Обработать нажатие Enter в поле ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.submit(line)

    def write(self, text: str):
        """Дописать текст в область вывода."""
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def submit(self, line: str):
        """Выполнить строку так, как будто её ввёл пользователь."""
        self.write(f"{self.shell.prompt()}{line}\n")
        result = self.shell.execute(line)
        self.write(with_newline(result.output))
        self._refresh_prompt()
        if result.exit_requested:
            self.root.destroy()

    def run(self):
        """Запустить главный цикл окна."""
        self.root.mainloop()
