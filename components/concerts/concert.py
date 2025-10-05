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