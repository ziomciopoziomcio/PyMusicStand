import tkinter as tk
import json
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class MainScreen(tk.Tk):
    def __init__(self):
        """
        Initialize the main screen of the electronic music stand application.
        """
        super().__init__()
        self.title("Electronic music stand")
        self.attributes('-fullscreen', True)
        self.generate_top_bar()
        self.mainloop()

    def generate_top_bar(self):
        """
        Generate a custom top bar with a red X button on the right.
        """
        top_bar = tk.Frame(self, bg='#f0f0f0', height=30)
        top_bar.pack(side='top', fill='x')

        # Optionally, add a label or menu on the left
        left_label = tk.Label(top_bar, text="Menu", bg='#f0f0f0', font=("Arial", 12))
        left_label.pack(side='left', padx=10)

        # Red X button on the right
        close_btn = tk.Button(top_bar, text="X", command=self.quit, bg='red', fg='white',
                             font=("Arial", 12, "bold"), bd=0, padx=10, pady=2, activebackground='#cc0000')
        close_btn.pack(side='right', padx=10, pady=2)

    def quit(self):
        """
        Quit the application.
        """
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.destroy()

MainScreen()