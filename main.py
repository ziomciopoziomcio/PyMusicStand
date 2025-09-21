import tkinter as tk
from tkinter import messagebox

from components.practice_mode.main_gui import GuiPracticeMode
from components.clock_controller import ClockController
from components.settings import Settings


class MainScreen(tk.Tk):
    def __init__(self):
        """
        Initialize the main screen of the electronic music stand application.
        """
        super().__init__()
        self.practice_mode_class = GuiPracticeMode(self)
        self.settings_class = Settings(self)
        self.clock_label = None
        self.selected_mode = None
        self.key_prev = None
        self.key_next = None
        self.set_keys()
        self.title("Electronic music stand")
        self.attributes('-fullscreen', True)
        self._clock_controller = ClockController(lambda: self.clock_label)
        self.generate_top_bar()
        self.generate_mode_selection()
        self.mainloop()

    def set_keys(self):
        """
        Set the key bindings for next and previous page.
        """
        self.settings_class.open_file()
        self.key_next = self.settings_class.key_next
        self.key_prev = self.settings_class.key_previous

    def generate_top_bar(self):
        """
        Generate a custom top bar with:
        - a red X button on the right.
        - clock on the left.
        - settings button
        """
        top_bar = tk.Frame(self, bg='#f0f0f0', height=30)
        top_bar.pack(side='top', fill='x')

        # Optionally, add a label or menu on the left
        left_label = tk.Label(top_bar, text="Menu", bg='#f0f0f0', font=("Arial", 12))
        left_label.pack(side='left', padx=10)

        # Red X button on the right
        close_btn = tk.Button(top_bar, text="X", command=self.quit, bg='red', fg='white',
                              font=("Arial", 12, "bold"), bd=0, padx=10, pady=2,
                              activebackground='#cc0000')
        close_btn.pack(side='right', padx=10, pady=2)

        # Clock on the left
        self.clock_label = tk.Label(top_bar, text="", bg='#f0f0f0', font=("Arial", 12))
        self.clock_label.pack(side='left', padx=10)

        self._clock_controller.set_label()

        # Settings button
        settings_btn = tk.Button(top_bar, text="Settings", command=self.settings_class.open_settings,
                                 bg='#f0f0f0', fg='black', font=("Arial", 12), bd=0, padx=10, pady=2)
        settings_btn.pack(side='right', padx=10, pady=2)

    def quit(self):
        """
        Quit the application.
        """
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.destroy()

    def generate_mode_selection(self):
        """
        Generate mode selection buttons in the center of the screen.
        Modes: "Concert", "Practice"
        """

        mode_frame = tk.Frame(self)
        mode_frame.pack(expand=True)

        concert_btn = tk.Button(mode_frame, text="Concert", font=("Arial", 24), width=15, height=3,
                                command=lambda: self.select_mode(0))
        concert_btn.grid(row=0, column=0, padx=20, pady=20)

        practice_btn = tk.Button(mode_frame, text="Practice", font=("Arial", 24), width=15,
                                 height=3,
                                 command=lambda: self.select_mode(1))
        practice_btn.grid(row=0, column=1, padx=20, pady=20)

    def select_mode(self, mode: int):
        """
        Handle mode selection.
        :param mode: 0 for Concert, 1 for Practice
        """
        modes = {0: "Concert", 1: "Practice"}
        if mode not in modes:
            messagebox.showerror("Error", "Invalid mode selected.")
            return
        if mode == 0:
            # Concert mode selected
            self.selected_mode = modes.get(mode, "Unknown")
            messagebox.showinfo("Mode Selected",
                                f"You have selected {self.selected_mode} mode.\n Currently under development.")
        elif mode == 1:
            # Practice mode selected
            self.selected_mode = modes.get(mode, "Unknown")
            self.practice_mode_class.change_to_practice_mode()

    def clear_screen(self):
        """
        Clear all widgets from the main screen.
        """
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == '__main__':
    app = MainScreen()
