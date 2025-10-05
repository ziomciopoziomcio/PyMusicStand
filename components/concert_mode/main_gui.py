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

        # Scrollable concerts list
        container = tk.Frame(self.master)
        container.pack(pady=10, fill='both', expand=True)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        concerts_frame = tk.Frame(canvas)

        concerts_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=concerts_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        # Scrollable scores list for program selection
        program_container = tk.Frame(form_frame)
        program_container.grid(row=4, column=0, columnspan=2, sticky='nsew')
        program_canvas = tk.Canvas(program_container, height=250)
        program_scrollbar = tk.Scrollbar(program_container, orient="vertical", command=program_canvas.yview)
        program_scores_frame = tk.Frame(program_canvas)

        program_scores_frame.bind(
            "<Configure>",
            lambda e: program_canvas.configure(
                scrollregion=program_canvas.bbox("all")
            )
        )
        program_canvas.create_window((0, 0), window=program_scores_frame, anchor="nw")
        program_canvas.configure(yscrollcommand=program_scrollbar.set)

        program_canvas.pack(side="left", fill="both", expand=True)
        program_scrollbar.pack(side="right", fill="y")

        scores = self.scores_manager.list_scores()
        program_vars = []
        for i, score in enumerate(scores):
            var = tk.IntVar()
            cb = tk.Checkbutton(program_scores_frame, text=score.name, variable=var, font=("Arial", 12))
            cb.pack(anchor='w')
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
        open_btn = tk.Button(btn_frame, text="Open Concert", font=("Arial", 14),
                             command=lambda: self.open_concert_viewer(concert))
        open_btn.pack(side='left', padx=10)
        edit_btn = tk.Button(btn_frame, text="Edit", font=("Arial", 14),
                             command=lambda: self.edit_concert(uid))
        edit_btn.pack(side='left', padx=10)
        delete_btn = tk.Button(btn_frame, text="Delete", font=("Arial", 14),
                               command=lambda: self.delete_concert(uid))
        delete_btn.pack(side='left', padx=10)
        back_btn = tk.Button(btn_frame, text="Back", font=("Arial", 14),
                             command=self.generate_mode_gui)
        back_btn.pack(side='left', padx=10)

    def open_concert_viewer(self, concert, score_index=0, last=False):
        """
        Open the concert program in a PDF viewer, similar to practice mode.
        Only scores from the concert program are shown.
        """
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.add_title_to_top_bar(concert.name)
        self.master.title(f"Concert: {concert.name}")

        program_scores = [self.scores_manager.get_score(uid) for uid in concert.program]
        program_scores = [s for s in program_scores if s is not None]

        if not program_scores:
            label = tk.Label(self.master, text="No scores in concert program.", font=("Arial", 20), fg="red")
            label.pack(pady=40)
            back_button = tk.Button(self.master, text="Back", font=("Arial", 14),
                                    command=lambda: self.view_concert_details(concert.UID))
            back_button.pack(pady=20)
            return

        def go_prev(event=None):
            if getattr(self, '_pdf_doc', None) and self._pdf_page > 0:
                self._pdf_page -= 1
                show_page(self._pdf_page)
            else:
                self.open_concert_viewer(concert, (self._score_index - 1) % len(program_scores), last=True)

        def go_next(event=None):
            if getattr(self, '_pdf_doc', None) and self._pdf_page < self._pdf_doc.page_count - 1:
                self._pdf_page += 1
                show_page(self._pdf_page)
            else:
                self.open_concert_viewer(concert, (self._score_index + 1) % len(program_scores))

        def bind_keys():
            self._unbind_prev = self.master.bind(self.master.key_prev, go_prev)
            self._unbind_next = self.master.bind(self.master.key_next, go_next)

        def unbind_keys():
            if hasattr(self, '_unbind_prev'):
                self.master.unbind(self.master.key_prev, self._unbind_prev)
            if hasattr(self, '_unbind_next'):
                self.master.unbind(self.master.key_next, self._unbind_next)

        bind_keys()

        def back_and_unbind():
            unbind_keys()
            self.view_concert_details(concert.UID)

        score = program_scores[score_index]
        self._score_index = score_index

        if not getattr(score, 'has_pdf', False) or not getattr(score, 'pdf_data', None):
            label = tk.Label(self.master, text="PDF unavailable", font=("Arial", 20), fg="red")
            label.pack(pady=40)
            nav_frame = tk.Frame(self.master)
            nav_frame.pack(pady=10)
            prev_btn = tk.Button(nav_frame, text="\u2190", font=("Arial", 18),
                                 command=lambda: self.open_concert_viewer(concert, (score_index - 1) % len(program_scores), last=True))
            prev_btn.pack(side='left', padx=20)
            next_btn = tk.Button(nav_frame, text="\u2192", font=("Arial", 18),
                                 command=lambda: self.open_concert_viewer(concert, (score_index + 1) % len(program_scores)))
            next_btn.pack(side='left', padx=20)
            back_button = tk.Button(nav_frame, text="Back", font=("Arial", 14),
                                    command=back_and_unbind)
            back_button.pack(side='left', padx=20)
            return

        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        # Left frame: program score list
        left_frame = tk.Frame(container, width=200, bg='#f0f0f0')
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)

        for i, s in enumerate(program_scores):
            is_selected = (i == score_index)
            btn_bg = 'lightblue' if is_selected else '#f0f0f0'
            btn_font = ("Arial", 12, "bold") if is_selected else ("Arial", 12)

            def make_open_func(idx=i):
                return lambda: self.open_concert_viewer(concert, idx)

            score_btn = tk.Button(left_frame, text=s.name, font=btn_font, width=20, anchor='w',
                                  bg=btn_bg, relief='flat', command=make_open_func())
            score_btn.pack(fill='x', pady=1, padx=2)

        # Right frame: PDF viewer and navigation
        right_frame = tk.Frame(container)
        right_frame.pack(side='left', fill='both', expand=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(score.pdf_data)
            pdf_path = tmp.name

        self._pdf_doc = fitz.open(pdf_path)
        self._pdf_page = 0
        if last:
            self._pdf_page = self._pdf_doc.page_count - 1
        self._pdf_score = score
        self._pdf_img_label = None
        self._pdf_path = pdf_path

        def show_page(page_num):
            page = self._pdf_doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img.thumbnail((900, 1200))
            tk_img = ImageTk.PhotoImage(img)
            if self._pdf_img_label is None:
                self._pdf_img_label = tk.Label(right_frame, image=tk_img)
                self._pdf_img_label.image = tk_img
                self._pdf_img_label.pack(pady=10)
            else:
                self._pdf_img_label.configure(image=tk_img)
                self._pdf_img_label.image = tk_img

        nav_frame = tk.Frame(right_frame)
        nav_frame.pack(pady=10)
        prev_btn = tk.Button(nav_frame, text="\u2190", font=("Arial", 18), command=go_prev)
        prev_btn.pack(side='left', padx=20)
        next_btn = tk.Button(nav_frame, text="\u2192", font=("Arial", 18), command=go_next)
        next_btn.pack(side='left', padx=20)
        back_button = tk.Button(nav_frame, text="Back", font=("Arial", 14), command=back_and_unbind)
        back_button.pack(side='left', padx=20)

        show_page(self._pdf_page)

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

        # Scrollable scores list for program selection
        program_container = tk.Frame(form_frame)
        program_container.grid(row=4, column=0, columnspan=2, sticky='nsew')
        program_canvas = tk.Canvas(program_container, height=250)
        program_scrollbar = tk.Scrollbar(program_container, orient="vertical", command=program_canvas.yview)
        program_scores_frame = tk.Frame(program_canvas)

        program_scores_frame.bind(
            "<Configure>",
            lambda e: program_canvas.configure(
                scrollregion=program_canvas.bbox("all")
            )
        )
        program_canvas.create_window((0, 0), window=program_scores_frame, anchor="nw")
        program_canvas.configure(yscrollcommand=program_scrollbar.set)

        program_canvas.pack(side="left", fill="both", expand=True)
        program_scrollbar.pack(side="right", fill="y")

        scores = self.scores_manager.list_scores()
        program_vars = []
        for i, score in enumerate(scores):
            var = tk.IntVar(value=1 if score.UID in concert.program else 0)
            cb = tk.Checkbutton(program_scores_frame, text=score.name, variable=var, font=("Arial", 12))
            cb.pack(anchor='w')
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
