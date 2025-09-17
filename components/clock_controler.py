import threading
import time
import tkinter as tk


def clock_controller(master: tk.Tk, clock_label: tk.Label):
    """
    Update the clock label every second in a separate thread.
    :param master: The main Tkinter window.
    :param clock_label: The label to update with the current time.
    """

    def update_clock():
        while True:
            current_time = time.strftime("%H:%M:%S")
            current_date = time.strftime("%d.%m.%Y")
            clock_label.config(text=f"{current_date} {current_time}")
            time.sleep(1)

    threading.Thread(target=update_clock, daemon=True).start()
