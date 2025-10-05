import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import time

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
        self.break_timer_state = {}  # {concert_uid: {index: {"start_time": ..., "duration": ...}}}

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

        # Program list with order controls
        program_frame = tk.Frame(details_frame)
        program_frame.pack(anchor='w')
        for idx, item in enumerate(concert.program):
            if isinstance(item, dict) and item.get("type") == "break":
                duration = item.get("duration", 300)
                row = tk.Frame(program_frame)
                row.pack(fill='x', pady=1)
                tk.Label(row, text=f"{idx+1}. --- Break ({duration//60} min) ---", font=("Arial", 12, "italic"), width=30, anchor='w', fg="gray").pack(side='left')
                up_btn = tk.Button(row, text="↑", font=("Arial", 10),
                                   command=lambda i=idx: self.move_program_item(uid, i, i-1))
                up_btn.pack(side='left')
                down_btn = tk.Button(row, text="↓", font=("Arial", 10),
                                     command=lambda i=idx: self.move_program_item(uid, i, i+1))
                down_btn.pack(side='left')
                del_btn = tk.Button(row, text="✕", font=("Arial", 10),
                                    command=lambda i=idx: self.remove_program_item(uid, i))
                del_btn.pack(side='left')
            else:
                score = self.scores_manager.get_score(item)
                score_name = score.name if score else f"Unknown ({item})"
                row = tk.Frame(program_frame)
                row.pack(fill='x', pady=1)
                tk.Label(row, text=f"{idx+1}. {score_name}", font=("Arial", 12), width=30, anchor='w').pack(side='left')
                up_btn = tk.Button(row, text="↑", font=("Arial", 10),
                                   command=lambda i=idx: self.move_program_item(uid, i, i-1))
                up_btn.pack(side='left')
                down_btn = tk.Button(row, text="↓", font=("Arial", 10),
                                     command=lambda i=idx: self.move_program_item(uid, i, i+1))
                down_btn.pack(side='left')
                del_btn = tk.Button(row, text="✕", font=("Arial", 10),
                                    command=lambda i=idx: self.remove_program_item(uid, i))
                del_btn.pack(side='left')

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

    def move_program_item(self, concert_uid, from_index, to_index):
        concert = self.concerts_manager.get_concert(concert_uid)
        if concert and 0 <= from_index < len(concert.program) and 0 <= to_index < len(concert.program):
            self.concerts_manager.move_program_item(concert_uid, from_index, to_index)
            self.concerts_manager.save()
            self.view_concert_details(concert_uid)

    def remove_program_item(self, concert_uid, index):
        concert = self.concerts_manager.get_concert(concert_uid)
        if concert and 0 <= index < len(concert.program):
            self.concerts_manager.remove_program_item(concert_uid, index)
            self.concerts_manager.save()
            self.view_concert_details(concert_uid)

    def open_concert_viewer(self, concert, score_index=0, last=False):
        """
        Open the concert program in a PDF viewer, similar to practice mode.
        Only scores from the concert program are shown.
        """
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.add_title_to_top_bar(concert.name)
        self.master.title(f"Concert: {concert.name}")

        # Filter program items for display
        program_items = concert.program
        display_items = []
        for item in program_items:
            if isinstance(item, dict) and item.get("type") == "break":
                display_items.append(item)
            else:
                score = self.scores_manager.get_score(item)
                if score:
                    display_items.append(score)
        if not display_items:
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
                self.open_concert_viewer(concert, (self._score_index - 1) % len(display_items), last=True)

        def go_next(event=None):
            if getattr(self, '_pdf_doc', None) and self._pdf_page < self._pdf_doc.page_count - 1:
                self._pdf_page += 1
                show_page(self._pdf_page)
            else:
                self.open_concert_viewer(concert, (self._score_index + 1) % len(display_items))

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

        item = display_items[score_index]
        self._score_index = score_index

        # --- BREAK PAGE ---
        if isinstance(item, dict) and item.get("type") == "break":
            duration = item.get("duration", 300)
            concert_uid = concert.UID
            break_idx = score_index

            if concert_uid not in self.break_timer_state:
                self.break_timer_state[concert_uid] = {}
            timer_state = self.break_timer_state[concert_uid].get(break_idx, {})
            running = [False]
            start_time = timer_state.get("start_time")
            duration_sec = timer_state.get("duration", duration)

            def save_timer_state(start_time, duration):
                self.break_timer_state[concert_uid][break_idx] = {
                    "start_time": start_time,
                    "duration": duration
                }

            def clear_timer_state():
                if break_idx in self.break_timer_state.get(concert_uid, {}):
                    del self.break_timer_state[concert_uid][break_idx]

            label = tk.Label(self.master, text=f"Break\n{duration_sec//60}:{duration_sec%60:02d} min", font=("Arial", 32), fg="gray")
            label.pack(pady=40)

            # Edit break duration
            edit_frame = tk.Frame(self.master)
            edit_frame.pack(pady=5)
            tk.Label(edit_frame, text="Edit break duration (min):", font=("Arial", 12)).pack(side='left')
            duration_entry = tk.Entry(edit_frame, font=("Arial", 12), width=5)
            duration_entry.insert(0, str(duration_sec // 60))
            duration_entry.pack(side='left')
            def save_duration():
                try:
                    new_duration = int(duration_entry.get()) * 60
                    concert.program[score_index]["duration"] = new_duration
                    self.concerts_manager.save()
                    if running[0]:
                        save_timer_state(start_time, new_duration)
                    self.open_concert_viewer(concert, score_index)
                except Exception:
                    messagebox.showerror("Error", "Invalid duration.")
            save_btn = tk.Button(edit_frame, text="Save", font=("Arial", 12), command=save_duration)
            save_btn.pack(side='left', padx=5)

            timer_label = tk.Label(self.master, text="", font=("Arial", 24), fg="blue")
            timer_label.pack(pady=10)

            def update_timer():
                if not running[0]:
                    return
                # Check if timer_label still exists
                try:
                    now = time.time()
                    elapsed = int(now - start_time)
                    left = duration_sec - elapsed
                    if left >= 0:
                        mins = left // 60
                        secs = left % 60
                        timer_label.config(text=f"{mins}:{secs:02d}")
                    else:
                        mins = (-left) // 60
                        secs = (-left) % 60
                        timer_label.config(text=f"Break finished! -{mins}:{secs:02d}")
                    # Only schedule next update if label still exists
                    if str(timer_label) in timer_label.master.tk.call('winfo', 'children', timer_label.master._w):
                        self.master.after(1000, update_timer)
                except tk.TclError:
                    # Widget was destroyed, stop timer
                    running[0] = False

            def start_break():
                running[0] = True
                nonlocal start_time
                start_time = time.time()
                save_timer_state(start_time, duration_sec)
                update_timer()

            # If timer was running, resume
            if start_time and running[0] is False:
                running[0] = True
                update_timer()

            start_btn = tk.Button(self.master, text="Start Break", font=("Arial", 14), command=start_break)
            start_btn.pack(pady=5)

            nav_frame = tk.Frame(self.master)
            nav_frame.pack(pady=10)
            def stop_and_switch(func):
                running[0] = False
                clear_timer_state()
                func()
            prev_btn = tk.Button(nav_frame, text="\u2190", font=("Arial", 18),
                                 command=lambda: stop_and_switch(lambda: self.open_concert_viewer(concert, (score_index - 1) % len(display_items), last=True)))
            prev_btn.pack(side='left', padx=20)
            next_btn = tk.Button(nav_frame, text="\u2192", font=("Arial", 18),
                                 command=lambda: stop_and_switch(lambda: self.open_concert_viewer(concert, (score_index + 1) % len(display_items))))
            next_btn.pack(side='left', padx=20)
            back_button = tk.Button(nav_frame, text="Back", font=("Arial", 14),
                                    command=lambda: stop_and_switch(lambda: self.view_concert_details(concert.UID)))
            back_button.pack(side='left', padx=20)
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(item.pdf_data)
            pdf_path = tmp.name

        self._pdf_doc = fitz.open(pdf_path)
        self._pdf_page = 0
        if last:
            self._pdf_page = self._pdf_doc.page_count - 1
        self._pdf_score = item
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

        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        # Left frame: program score list
        left_frame = tk.Frame(container, width=200, bg='#f0f0f0')
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)
        for i, s in enumerate(display_items):
            is_selected = (i == score_index)
            btn_bg = 'lightblue' if is_selected else '#f0f0f0'
            btn_font = ("Arial", 12, "bold") if is_selected else ("Arial", 12)
            if isinstance(s, dict) and s.get("type") == "break":
                btn_text = f"--- Break ({s.get('duration',300)//60} min) ---"
            else:
                btn_text = s.name
            def make_open_func(idx=i):
                return lambda: self.open_concert_viewer(concert, idx)
            score_btn = tk.Button(left_frame, text=btn_text, font=btn_font, width=20, anchor='w',
                                  bg=btn_bg, relief='flat', command=make_open_func())
            score_btn.pack(fill='x', pady=1, padx=2)

        # Right frame: PDF viewer and navigation
        right_frame = tk.Frame(container)
        right_frame.pack(side='left', fill='both', expand=True)

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

        # Scrollable scores list for selection
        program_label = tk.Label(form_frame, text="Available scores:", font=("Arial", 14))
        program_label.grid(row=3, column=0, padx=5, pady=5)

        program_container = tk.Frame(form_frame)
        program_container.grid(row=4, column=0, columnspan=2, sticky='nsew')
        program_canvas = tk.Canvas(program_container, height=150)
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
        score_vars = []
        for i, score in enumerate(scores):
            var = tk.IntVar(value=score.UID in [item for item in concert.program if not isinstance(item, dict)])
            cb = tk.Checkbutton(program_scores_frame, text=score.name, variable=var, font=("Arial", 12))
            cb.pack(anchor='w')
            score_vars.append((var, score.UID))

        # Program order editor (scrollable)
        order_label = tk.Label(form_frame, text="Program order (songs & breaks):", font=("Arial", 14))
        order_label.grid(row=5, column=0, columnspan=2, pady=(10,0))

        order_container = tk.Frame(form_frame)
        order_container.grid(row=6, column=0, columnspan=2, sticky='nsew')
        order_canvas = tk.Canvas(order_container, height=180)
        order_scrollbar = tk.Scrollbar(order_container, orient="vertical", command=order_canvas.yview)
        order_frame = tk.Frame(order_canvas)

        order_frame.bind(
            "<Configure>",
            lambda e: order_canvas.configure(
                scrollregion=order_canvas.bbox("all")
            )
        )
        order_canvas.create_window((0, 0), window=order_frame, anchor="nw")
        order_canvas.configure(yscrollcommand=order_scrollbar.set)

        order_canvas.pack(side="left", fill="both", expand=True)
        order_scrollbar.pack(side="right", fill="y")

        # Show current program order (songs and breaks)
        for idx, item in enumerate(concert.program):
            row = tk.Frame(order_frame)
            row.pack(fill='x', pady=1)
            if isinstance(item, dict) and item.get("type") == "break":
                duration = item.get("duration", 300)
                tk.Label(row, text=f"{idx+1}. --- Break ({duration//60} min) ---", font=("Arial", 12, "italic"), width=30, anchor='w', fg="gray").pack(side='left')
            else:
                score = self.scores_manager.get_score(item)
                score_name = score.name if score else f"Unknown ({item})"
                tk.Label(row, text=f"{idx+1}. {score_name}", font=("Arial", 12), width=30, anchor='w').pack(side='left')
            up_btn = tk.Button(row, text="↑", font=("Arial", 10),
                               command=lambda i=idx: self.move_program_item(uid, i, i-1))
            up_btn.pack(side='left')
            down_btn = tk.Button(row, text="↓", font=("Arial", 10),
                                 command=lambda i=idx: self.move_program_item(uid, i, i+1))
            down_btn.pack(side='left')
            del_btn = tk.Button(row, text="✕", font=("Arial", 10),
                                command=lambda i=idx: self.remove_program_item(uid, i))
            del_btn.pack(side='left')

        # Add break controls
        break_control_frame = tk.Frame(form_frame)
        break_control_frame.grid(row=7, column=0, columnspan=2, pady=10)
        tk.Label(break_control_frame, text="Add Break:", font=("Arial", 12)).pack(side='left')
        break_duration_entry = tk.Entry(break_control_frame, font=("Arial", 12), width=5)
        break_duration_entry.insert(0, "5")  # default 5 min
        break_duration_entry.pack(side='left')
        tk.Label(break_control_frame, text="min at position", font=("Arial", 12)).pack(side='left')
        break_pos_entry = tk.Entry(break_control_frame, font=("Arial", 12), width=3)
        break_pos_entry.pack(side='left')
        def add_break_btn_action():
            try:
                pos = int(break_pos_entry.get())
                duration = int(break_duration_entry.get()) * 60
                self.concerts_manager.add_break(uid, pos, duration)
                self.concerts_manager.save()
                self.edit_concert(uid)
            except Exception:
                messagebox.showerror("Error", "Invalid break position or duration.")
        add_break_btn = tk.Button(break_control_frame, text="Add", font=("Arial", 12), command=add_break_btn_action)
        add_break_btn.pack(side='left', padx=5)

        def submit():
            name = name_entry.get()
            date = date_entry.get()
            location = location_entry.get()
            # Only keep checked scores, preserve breaks
            checked_uids = [uid for var, uid in score_vars if var.get()]
            new_program = []
            for item in concert.program:
                if isinstance(item, dict) and item.get("type") == "break":
                    new_program.append(item)
                elif item in checked_uids:
                    new_program.append(item)
            # Add any newly checked scores not already in program
            for uid in checked_uids:
                if uid not in new_program:
                    new_program.append(uid)
            if not name or not date or not location:
                messagebox.showerror("Error", "Please fill all fields.")
                return
            self.concerts_manager.update_concert(concert.UID, name, date, location, new_program)
            self.concerts_manager.save()
            # Reload concert object before showing details
            updated_concert = self.concerts_manager.get_concert(concert.UID)
            if updated_concert:
                self.view_concert_details(updated_concert.UID)
            else:
                messagebox.showerror("Error", "Concert not found after update.")

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
