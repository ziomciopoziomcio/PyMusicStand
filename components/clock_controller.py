import threading
import time
import tkinter as tk


class ClockController:
    def __init__(self, get_label_func):
        self.current_date = time.strftime("%d.%m.%Y")
        self.current_time = time.strftime("%H:%M:%S")
        self.get_label_func = get_label_func
        self._running = True
        self.thread = threading.Thread(target=self.update_clock, daemon=True)
        self.thread.start()

    def set_label(self):
        label = self.get_label_func()
        label.config(text=f"{self.current_date} {self.current_time}")

    def update_clock(self):
        while self._running:
            label = self.get_label_func()
            if label is not None:
                self.current_time = time.strftime("%H:%M:%S")
                self.current_date = time.strftime("%d.%m.%Y")
                try:
                    label.config(text=f"{self.current_date} {self.current_time}")
                except Exception:
                    time.sleep(5)
                    continue
            time.sleep(1)

    def stop(self):
        self._running = False

