import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

import pymupdf as fitz
from PIL import Image, ImageTk

sys.path.append("..")

from components.scores.scores_manager import ScoresManager
from components.concerts.concerts_manager import ConcertsManager

class GuiConcertMode:
    def __init__(self, master):
        self.master = master
        self.concerts_manager = ConcertsManager()
        self.concerts_manager.load()
        self.scores_manager = ScoresManager()
        self.scores_manager.load()

    def change_to_concert_mode(self):
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Concert mode")
        self.generate_mode_gui()

    def generate_mode_gui(self):
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Concert mode")

        concerts_frame = tk.Frame(self.master)
        concerts_frame.pack(pady=10, fill='both', expand=True)

        concerts_list = self.concerts_manager.list_concerts()
        for concert in concerts_list:
            def make_view_func(uid=concert.UID):
                return lambda: self.view_concert_details(uid)
            concert_btn = tk.Button(concerts_frame, text=f"{concert.name} ({concert.date})", font=("Arial", 12), width=40,
                                    command=make_view_func())
            concert_btn.pack(pady=2)

        add_btn = tk.Button(self.master, text="Add Concert", font=("Arial", 14), command=self.add_concert)
        add_btn.pack(pady=5)

        back_btn = tk.Button(self.master, text="Back", font=("Arial", 14),
                             command=self.master.generate_mode_selection)
        back_btn.pack(pady=5)

    def add_concert(self):
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Add Concert")

        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=20)

        name_label = tk.Label(form_frame, text="Concert Name:", font=("Arial", 14))
        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(form_frame, font=("Arial", 14))
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        date_label = tk.Label(form_frame, text="Date:", font=("Arial", 14))
        date_label.grid(row=1, column=0, padx=5, pady=5)
        date_entry = tk.Entry(form_frame, font=("Arial", 14))
        date_entry.grid(row=1, column=1, padx=5, pady=5)

        location_label = tk.Label(form_frame, text="Location:", font=("Arial", 14))
        location_label.grid(row=2, column=0, padx=5, pady=5)
        location_entry = tk.Entry(form_frame, font=("Arial", 14))
        location_entry.grid(row=2, column=1, padx=5, pady=5)

        program_label = tk.Label(form_frame, text="Program (select scores):", font=("Arial", 14))
        program_label.grid(row=3, column=0, padx=5, pady=5)
        scores = self.scores_manager.list_scores()
        program_vars = []
        for i, score in enumerate(scores):
            var = tk.IntVar()
            cb = tk.Checkbutton(form_frame, text=score.name, variable=var, font=("Arial", 12))
            cb.grid(row=4 + i, column=1, sticky='w')
            program_vars.append((var, score.UID))

        def submit():
            name = name_entry.get()
            date = date_entry.get()
            location = location_entry.get()
            program = [uid for var, uid in program_vars if var.get()]
            if not name or not date or not location:
                messagebox.showerror("Error", "Please fill all fields.")
                return
            self.concerts_manager.add_concert(name, date, location, program)
            self.concerts_manager.save()
            self.generate_mode_gui()

        submit_btn = tk.Button(self.master, text="Submit", font=("Arial", 14), command=submit)
        submit_btn.pack(pady=10)

        cancel_btn = tk.Button(self.master, text="Cancel", font=("Arial", 14),
                               command=self.generate_mode_gui)
        cancel_btn.pack(pady=5)

    def view_concert_details(self, uid):
        concert = self.concerts_manager.get_concert(uid)
        if not concert:
            messagebox.showerror("Error", "Concert not found.")
            return
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title(f"Concert: {concert.name}")

        details_frame = tk.Frame(self.master)
        details_frame.pack(pady=20)

        tk.Label(details_frame, text=f"Name: {concert.name}", font=("Arial", 14)).pack(anchor='w')
        tk.Label(details_frame, text=f"Date: {concert.date}", font=("Arial", 14)).pack(anchor='w')
        tk.Label(details_frame, text=f"Location: {concert.location}", font=("Arial", 14)).pack(anchor='w')
        tk.Label(details_frame, text="Program:", font=("Arial", 14, "bold")).pack(anchor='w', pady=(10,0))
        for uid in concert.program:
            score = self.scores_manager.get_score(uid)
            score_name = score.name if score else f"Unknown ({uid})"
            tk.Label(details_frame, text=f"- {score_name}", font=("Arial", 12)).pack(anchor='w')

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)
        edit_btn = tk.Button(btn_frame, text="Edit", font=("Arial", 14),
                             command=lambda: self.edit_concert(uid))
        edit_btn.pack(side='left', padx=10)
        delete_btn = tk.Button(btn_frame, text="Delete", font=("Arial", 14),
                               command=lambda: self.delete_concert(uid))
        delete_btn.pack(side='left', padx=10)
        back_btn = tk.Button(btn_frame, text="Back", font=("Arial", 14),
                             command=self.generate_mode_gui)
        back_btn.pack(side='left', padx=10)

    def edit_concert(self, uid):
        concert = self.concerts_manager.get_concert(uid)
        if not concert:
            messagebox.showerror("Error", "Concert not found.")
            return
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title(f"Edit Concert: {concert.name}")

        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=20)

        name_label = tk.Label(form_frame, text="Concert Name:", font=("Arial", 14))
        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(form_frame, font=("Arial", 14))
        name_entry.insert(0, concert.name)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        date_label = tk.Label(form_frame, text="Date:", font=("Arial", 14))
        date_label.grid(row=1, column=0, padx=5, pady=5)
        date_entry = tk.Entry(form_frame, font=("Arial", 14))
        date_entry.insert(0, concert.date)
        date_entry.grid(row=1, column=1, padx=5, pady=5)

        location_label = tk.Label(form_frame, text="Location:", font=("Arial", 14))
        location_label.grid(row=2, column=0, padx=5, pady=5)
        location_entry = tk.Entry(form_frame, font=("Arial", 14))
        location_entry.insert(0, concert.location)
        location_entry.grid(row=2, column=1, padx=5, pady=5)

        program_label = tk.Label(form_frame, text="Program (select scores):", font=("Arial", 14))
        program_label.grid(row=3, column=0, padx=5, pady=5)
        scores = self.scores_manager.list_scores()
        program_vars = []
        for i, score in enumerate(scores):
            var = tk.IntVar(value=1 if score.UID in concert.program else 0)
            cb = tk.Checkbutton(form_frame, text=score.name, variable=var, font=("Arial", 12))
            cb.grid(row=4 + i, column=1, sticky='w')
            program_vars.append((var, score.UID))

        def submit():
            name = name_entry.get()
            date = date_entry.get()
            location = location_entry.get()
            program = [uid for var, uid in program_vars if var.get()]
            if not name or not date or not location:
                messagebox.showerror("Error", "Please fill all fields.")
                return
            self.concerts_manager.update_concert(uid, name, date, location, program)
            self.concerts_manager.save()
            self.view_concert_details(uid)

        submit_btn = tk.Button(self.master, text="Save", font=("Arial", 14), command=submit)
        submit_btn.pack(pady=10)

        cancel_btn = tk.Button(self.master, text="Cancel", font=("Arial", 14),
                               command=lambda: self.view_concert_details(uid))
        cancel_btn.pack(pady=5)

    def delete_concert(self, uid):
        concert = self.concerts_manager.get_concert(uid)
        if not concert:
            messagebox.showerror("Error", "Concert not found.")
            return
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{concert.name}'?"):
            self.concerts_manager.remove_concert(uid)
            self.concerts_manager.save()
            self.generate_mode_gui()
