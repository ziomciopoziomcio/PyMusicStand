import tkinter as tk
import sys
from tkinter import filedialog, messagebox
import tempfile
import pymupdf as fitz
from PIL import Image, ImageTk

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
            def make_open_func(uid=score.UID):
                return lambda: self.open_score(uid)
            score_button = tk.Button(scores_frame, text=score.name, font=("Arial", 12), width=30, command=make_open_func())
            score_button.pack(pady=2)


        add_button = tk.Button(self.master, text="Add Score", font=("Arial", 14), command=self.add_score)
        add_button.pack(pady=5)

        remove_button = tk.Button(self.master, text="Remove Score", font=("Arial", 14), command=self.remove_score)
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

    def remove_score(self):
        """
        Remove a score from the scores manager.
        1. Clear the current screen.
        2. Show a list of scores with options to select one for removal.
        3. On selection, remove the score from the manager. (Ask for confirmation)
        4. Return to the practice mode GUI.
        """
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.title("Remove Score")

        scores_frame = tk.Frame(self.master)
        scores_frame.pack(pady=10, fill='both', expand=True)

        scores_list = self.scores_manager.list_scores()
        for score in scores_list:
            def make_remove_func(s=score):
                def remove_func():
                    if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{s.name}'?"):
                        self.scores_manager.remove_score(s.UID)
                        self.scores_manager.save()
                        self.change_to_practice_mode()
                return remove_func

            score_button = tk.Button(scores_frame, text=score.name, font=("Arial", 12), width=30, command=make_remove_func())
            score_button.pack(pady=2)

        back_button = tk.Button(self.master, text="Back", font=("Arial", 14), command=self.change_to_practice_mode)
        back_button.pack(pady=5)

    def open_score(self, uid, last=False):
        """
        Open the score's PDF by UID, if available, in a tkinter PDF viewer.
        """
        score = next((s for s in self.scores_manager.list_scores() if s.UID == uid), None)
        if not score:
            messagebox.showerror("Error", "Score not found.")
            return
        self.show_pdf_viewer(score, uid, last=last)

    def show_pdf_viewer(self, score, uid, last=False):
        """
        Show a PDF viewer for the given score in the tkinter window.
        """
        self.master.clear_screen()
        self.master.generate_top_bar()
        self.master.add_title_to_top_bar(score.name)
        self.master.title(f"Score: {score.name}")

        def go_prev(event=None):
            if getattr(self, '_pdf_doc', None) and self._pdf_page > 0:
                self._pdf_page -= 1
                show_page(self._pdf_page)
            else:
                self.open_previous_score(uid)

        def go_next(event=None):
            if getattr(self, '_pdf_doc', None) and self._pdf_page < self._pdf_doc.page_count - 1:
                self._pdf_page += 1
                show_page(self._pdf_page)
            else:
                self.open_next_score(uid)

        def bind_keys():
            self._unbind_prev = self.master.bind(self.master.key_prev, go_prev)
            self._unbind_next = self.master.bind(self.master.key_next, go_next)
        def unbind_keys():
            if hasattr(self, '_unbind_prev'):
                self.master.unbind(self.master.key_prev, self._unbind_prev)
            if hasattr(self, '_unbind_next'):
                self.master.unbind(self.master.key_next, self._unbind_next)

        # Always bind keys, even if no PDF
        bind_keys()

        # Unbind keys when leaving PDF viewer
        def back_and_unbind():
            unbind_keys()
            self.change_to_practice_mode()

        if not getattr(score, 'has_pdf', False) or not getattr(score, 'pdf_data', None):
            label = tk.Label(self.master, text="PDF unavailable", font=("Arial", 20), fg="red")
            label.pack(pady=40)
            nav_frame = tk.Frame(self.master)
            nav_frame.pack(pady=10)
            prev_btn = tk.Button(nav_frame, text="\u2190", font=("Arial", 18), command=lambda: self.open_previous_score(uid))
            prev_btn.pack(side='left', padx=20)
            next_btn = tk.Button(nav_frame, text="\u2192", font=("Arial", 18), command=lambda: self.open_next_score(uid))
            next_btn.pack(side='left', padx=20)
            back_button = tk.Button(nav_frame, text="Back", font=("Arial", 14), command=back_and_unbind)
            back_button.pack(side='left', padx=20)
            return

        # Main container frame
        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        # Left frame: score list
        left_frame = tk.Frame(container, width=200, bg='#f0f0f0')
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)

        scores_list = self.scores_manager.list_scores()
        for s in scores_list:
            is_selected = (s.UID == uid)
            btn_bg = 'lightblue' if is_selected else '#f0f0f0'
            btn_font = ("Arial", 12, "bold") if is_selected else ("Arial", 12)
            def make_open_func(score_uid=s.UID):
                return lambda: self.open_score(score_uid)
            score_btn = tk.Button(left_frame, text=s.name, font=btn_font, width=20, anchor='w', bg=btn_bg, relief='flat', command=make_open_func())
            score_btn.pack(fill='x', pady=1, padx=2)

        # Right frame: PDF viewer and navigation
        right_frame = tk.Frame(container)
        right_frame.pack(side='left', fill='both', expand=True)

        # Save PDF data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(score.pdf_data)
            pdf_path = tmp.name

        # Store state for navigation
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
            img.thumbnail((900, 1200))  # Resize for display
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

    def open_next_score(self, uid):
        """
        Open the next score in the list after the given UID.
        If at the end of the list, wrap around to the first score.
        :param uid: Current score UID.
        """
        scores = self.scores_manager.list_scores()
        if not scores:
            messagebox.showinfo("Info", "No scores available.")
            return
        current_index = next((i for i, s in enumerate(scores) if s.UID == uid), None)
        if current_index is None:
            messagebox.showerror("Error", "Current score not found.")
            return
        next_index = (current_index + 1) % len(scores)
        next_score = scores[next_index]
        self.open_score(next_score.UID)

    def open_previous_score(self, uid):
        """
        Open the previous score in the list before the given UID.
        :param uid: Current score UID.
        """
        scores = self.scores_manager.list_scores()
        if not scores:
            messagebox.showinfo("Info", "No scores available.")
            return
        current_index = next((i for i, s in enumerate(scores) if s.UID == uid), None)
        if current_index is None:
            messagebox.showerror("Error", "Current score not found.")
            return
        prev_index = (current_index - 1) % len(scores)
        prev_score = scores[prev_index]
        self.open_score(prev_score.UID, last=True)
