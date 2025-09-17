import tkinter as tk
import json
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class MainScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Electronic music stand")
        self.attributes('-fullscreen', True)
        self.mainloop()

MainScreen()