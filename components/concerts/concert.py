import json

class Concert:
    def __init__(self, uid: str, name: str, date: str, location: str, program: list):
        """
        Initialize a Concert object.
        :param uid: Unique identifier for the concert.
        :param name: Name of the concert.
        :param date: Date of the concert.
        :param location: Location of the concert.
        :param program: List of scores (by UID) in the concert program.
        """
        self.UID = uid
        self.name = name
        self.date = date
        self.location = location
        self.program = program  # List of score UIDs

    def to_json(self) -> str:
        """
        Convert the Concert object to a JSON string.
        :return: JSON representation of the Concert object.
        """
        return json.dumps({
            "UID": self.UID,
            "name": self.name,
            "date": self.date,
            "location": self.location,
            "program": self.program
        })

    def save(self):
        """
        Save the Concert object to a JSON file named after its UID.
        """
        with open(f"{self.UID}.json", "w") as f:
            f.write(self.to_json())

    def move_program_item(self, from_index, to_index):
        """
        Move a score in the program from one position to another.
        """
        if from_index < 0 or from_index >= len(self.program) or to_index < 0 or to_index >= len(self.program):
            return False
        item = self.program.pop(from_index)
        self.program.insert(to_index, item)
        return True

    def remove_program_item(self, index):
        """
        Remove a score from the program by index.
        """
        if 0 <= index < len(self.program):
            self.program.pop(index)
            return True
        return False

    def insert_program_item(self, index, score_uid):
        """
        Insert a score UID into the program at a specific index.
        """
        if 0 <= index <= len(self.program):
            self.program.insert(index, score_uid)
            return True
        return False
