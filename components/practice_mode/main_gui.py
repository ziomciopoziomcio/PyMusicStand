import tkinter as tk


class GuiPracticeMode():
    def __init__(self, master):
        self.master = master


    def change_to_practice_mode(self):
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Practice Mode")
        label = tk.Label(self.master, text="Practice Mode Activated", font=("Arial", 24))
        label.pack(expand=True)