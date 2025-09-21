import json
import tkinter as tk


class Settings():
    def __init__(self, master):
        """
        Initialize the settings of the electronic music stand application.
        :param master: The main application window.
        """
        self.master = master
        self.key_next = None
        self.key_previous = None
        self.open_file()

    def open_settings(self):
        """
        Open the settings window.
        """
        settings_window = SettingsScreen(self.master, self)
        settings_window.grab_set()

    def save_file(self):
        """
        Save settings to a JSON file.
        """
        settings_data = {
            "key_next": self.key_next,
            "key_previous": self.key_previous
        }
        with open("settings.json", "w") as f:
            json.dump(settings_data, f)

    def open_file(self):
        """
        Load settings from a JSON file if it exists, else create an empty settings file.
        """
        try:
            with open("settings.json", "r") as f:
                settings_data = json.load(f)
                self.key_next = settings_data.get("key_next", None)
                self.key_previous = settings_data.get("key_previous", None)
        except FileNotFoundError:
            with open("settings.json", "w") as f:
                empty_data = {
                    "key_next": "a",
                    "key_previous": "d"
                }
                self.key_next = "a"
                self.key_previous = "d"
                json.dump(empty_data, f)

    def get_settings_from_window(self, key_next, key_previous):
        """
        Get settings from the settings window.
        :param key_next: Key for next page.
        :param key_previous: Key for previous page.
        """
        self.key_next = key_next
        self.key_previous = key_previous
        self.save_file()
        self.master.set_keys()


class SettingsScreen(tk.Toplevel):
    def __init__(self, master, setting_handler):
        """
        Initialize the settings screen of the electronic music stand application.
        """
        super().__init__(master)
        self.setting_handler = setting_handler
        self.title("Settings")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        """
        Create widgets for the settings screen:
        - key_next binding
        - key_previous binding
        Save button
        """
        tk.Label(self, text="Settings", font=("Arial", 16)).pack(pady=10)

        # Key binding for next page
        tk.Label(self, text="Key for Next Page:").pack(pady=5)
        self.key_next_entry = tk.Entry(self)
        self.key_next_entry.pack(pady=5)
        if self.setting_handler.key_next:
            self.key_next_entry.insert(0, self.setting_handler.key_next)

        # Key binding for previous page
        tk.Label(self, text="Key for Previous Page:").pack(pady=5)
        self.key_previous_entry = tk.Entry(self)
        self.key_previous_entry.pack(pady=5)
        if self.setting_handler.key_previous:
            self.key_previous_entry.insert(0, self.setting_handler.key_previous)

        # Save button
        save_button = tk.Button(self, text="Save Settings", command=self.save_settings)
        save_button.pack(pady=20)

    def save_settings(self):
        """
        Save the settings and close the settings screen.
        """
        # Here you would typically save the settings to a file or apply them
        self.setting_handler.get_settings_from_window(
            self.key_next_entry.get(),
            self.key_previous_entry.get()
        )
        self.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    settings = Settings(root)
    settings.open_file()  # Load existing settings if available
    settings.open_settings()  # Open the settings window
    root.mainloop()
