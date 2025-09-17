import threading
import time
import tkinter as tk


class ClockController:
    def __init__(self, get_label_func):
        self.get_label_func = get_label_func
        self._running = True
        self.thread = threading.Thread(target=self.update_clock, daemon=True)
        self.thread.start()

    def set_label(self):
        label = self.get_label_func()
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        label.config(text=f"{current_date} {current_time}")

    def update_clock(self):
        while self._running:
            label = self.get_label_func()
            if label is not None:
                current_time = time.strftime("%H:%M:%S")
                current_date = time.strftime("%d.%m.%Y")
                try:
                    label.config(text=f"{current_date} {current_time}")
                except Exception:
                    pass  # label may have been destroyed
            time.sleep(1)

    def stop(self):
        self._running = False

