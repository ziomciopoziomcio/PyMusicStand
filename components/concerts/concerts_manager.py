import uuid
import json
from components.concerts.concert import Concert

class ConcertsManager:
    def __init__(self):
        self.concerts = {}

    def add_concert(self, name: str, date: str, location: str, program: list) -> Concert:
        """
        Add a new Concert to the manager.
        :param name: Name of the concert.
        :param date: Date of the concert.
        :param location: Location of the concert.
        :param program: List of scores (by UID) in the concert program.
        :return: The created Concert object.
        """
        uid = str(uuid.uuid4())
        concert = Concert(uid, name, date, location, program)
        self.concerts[uid] = concert
        return concert

    def get_concert(self, uid: str) -> Concert:
        """
        Retrieve a Concert by its UID.
        :param uid: Unique identifier of the concert.
        :return: The Concert object if found, else None.
        """
        return self.concerts.get(uid)

    def remove_concert(self, uid: str) -> bool:
        """
        Remove a Concert by its UID.
        :param uid: Unique identifier of the concert.
        :return: True if the concert was removed, else False.
        """
        if uid in self.concerts:
            del self.concerts[uid]
            return True
        return False

    def list_concerts(self) -> list:
        """
        List all concerts managed by the ConcertsManager.
        :return: A list of Concert objects.
        """
        return list(self.concerts.values())

    def save_all(self):
        """
        Save all concerts to individual JSON files named after their UIDs.
        """
        for concert in self.concerts.values():
            concert.save()

    def save(self):
        """
        Save all concerts to a single JSON file.
        """
        with open("all_concerts.json", "w") as f:
            data = []
            for concert in self.concerts.values():
                data.append({
                    "UID": concert.UID,
                    "name": concert.name,
                    "date": concert.date,
                    "location": concert.location,
                    "program": concert.program
                })
            f.write(json.dumps(data))

    def load(self):
        """
        Load concerts from a single JSON file.
        """
        try:
            with open("all_concerts.json", "r") as f:
                data = json.loads(f.read())
                for concert_dict in data:
                    concert = Concert(
                        concert_dict["UID"],
                        concert_dict["name"],
                        concert_dict["date"],
                        concert_dict["location"],
                        concert_dict["program"]
                    )
                    self.concerts[concert.UID] = concert
        except FileNotFoundError:
            pass
    def update_concert(self, uid: str, name: str = None, date: str = None, location: str = None, program: list = None) -> bool:
        """
        Update an existing Concert's details.
        :param uid: Unique identifier of the concert to update.
        :param name: New name of the concert (optional).
        :param date: New date of the concert (optional).
        :param location: New location of the concert (optional).
        :param program: New list of scores (by UID) in the concert program (optional).
        :return: True if the concert was updated, else False.
        """
        concert = self.get_concert(uid)
        if concert:
            if name is not None:
                concert.name = name
            if date is not None:
                concert.date = date
            if location is not None:
                concert.location = location
            if program is not None:
                concert.program = program
            return True
        return False

    def move_program_item(self, concert_uid, from_index, to_index):
        concert = self.get_concert(concert_uid)
        if concert:
            return concert.move_program_item(from_index, to_index)
        return False

    def remove_program_item(self, concert_uid, index):
        concert = self.get_concert(concert_uid)
        if concert:
            return concert.remove_program_item(index)
        return False

    def insert_program_item(self, concert_uid, index, score_uid_or_break):
        concert = self.get_concert(concert_uid)
        if concert:
            return concert.insert_program_item(index, score_uid_or_break)
        return False

    def add_break(self, concert_uid, index, duration=300):
        concert = self.get_concert(concert_uid)
        if concert:
            return concert.add_break(index, duration)
        return False
