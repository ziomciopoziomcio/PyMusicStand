import tkinter as tk
import sys
from tkinter import filedialog, messagebox

sys.path.append("..")

from components.scores.scores_manager import ScoresManager


class GuiPracticeMode():
    def __init__(self, master):
        self.master = master
        self.scores_manager = ScoresManager()
        self.scores_manager.load()


    def change_to_practice_mode(self):
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Practice Mode")
        self.generate_mode_gui()

    def generate_mode_gui(self):
        """
        Generate the GUI for practice mode.
        1. Search bar to find scores.
        2. List of scores with options to select, add, or remove.
        """
        search_frame = tk.Frame(self.master)
        search_frame.pack(pady=10)

        search_label = tk.Label(search_frame, text="Search Scores:", font=("Arial", 14))
        search_label.pack(side='left', padx=5)

        search_entry = tk.Entry(search_frame, font=("Arial", 14))
        search_entry.pack(side='left', padx=5)

        search_button = tk.Button(search_frame, text="Search", font=("Arial", 14))
        search_button.pack(side='left', padx=5)

        scores_frame = tk.Frame(self.master)
        scores_frame.pack(pady=10, fill='both', expand=True)

        scores_list = self.scores_manager.list_scores()
        for score in scores_list:
            score_button = tk.Button(scores_frame, text=score.name, font=("Arial", 12), width=30)
            score_button.pack(pady=2)


        add_button = tk.Button(self.master, text="Add Score", font=("Arial", 14), command=self.add_score)
        add_button.pack(pady=5)

        remove_button = tk.Button(self.master, text="Remove Score", font=("Arial", 14))
        remove_button.pack(pady=5)

    def add_score(self):
        """
        Add a new score to the scores manager.
        1. Clear the current screen.
        2. Show a form to input score details (name, has_pdf, pdf_data).
        3. On submission, create a new Score and add it to the manager.
        4. Return to the practice mode GUI.
        """
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Add New Score")

        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=20)

        name_label = tk.Label(form_frame, text="Score Name:", font=("Arial", 14))
        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(form_frame, font=("Arial", 14))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        # PDF selection variables and widgets
        pdf_path_var = tk.StringVar()
        pdf_data = None

        def choose_pdf():
            path = filedialog.askopenfilename(
                title="Select PDF file",
                filetypes=[("PDF files", "*.pdf")]
            )
            if path:
                pdf_path_var.set(path)
                pdf_label.config(text=path)
            else:
                pdf_path_var.set("")
                pdf_label.config(text="No file selected")

        pdf_button = tk.Button(form_frame, text="Choose PDF", font=("Arial", 12), command=choose_pdf)
        pdf_button.grid(row=1, column=0, padx=5, pady=5)
        pdf_label = tk.Label(form_frame, text="No file selected", font=("Arial", 10))
        pdf_label.grid(row=1, column=1, padx=5, pady=5)

        def submit():
            name = name_entry.get()
            pdf_data = None
            if pdf_path_var.get():
                try:
                    with open(pdf_path_var.get(), 'rb') as f:
                        pdf_data = f.read()
                    has_pdf = True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read PDF: {e}")
                    return
            else:
                has_pdf = False
                pdf_data = None
            self.scores_manager.add_score(name, has_pdf, pdf_data)
            self.scores_manager.save()
            self.change_to_practice_mode()

        submit_button = tk.Button(self.master, text="Submit", font=("Arial", 14), command=submit)
        submit_button.pack(pady=10)

        cancel_button = tk.Button(self.master, text="Cancel", font=("Arial", 14), command=self.change_to_practice_mode)
        cancel_button.pack(pady=5)
