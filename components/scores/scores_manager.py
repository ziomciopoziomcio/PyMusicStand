import uuid
import json
from score import Score

class ScoresManager:
    def __init__(self):
        self.scores = {}

    def add_score(self, name: str, has_pdf: bool, pdf_data: bytes = None) -> Score:
        """
        Add a new Score to the manager.
        :param name: Name of the score.
        :param has_pdf: Whether the score has an associated PDF.
        :param pdf_data: PDF data as bytes, if available.
        :return: The created Score object.
        """
        uid = str(uuid.uuid4())
        score = Score(uid, name, has_pdf, pdf_data)
        self.scores[uid] = score
        return score

    def get_score(self, uid: str) -> Score:
        """
        Retrieve a Score by its UID.
        :param uid: Unique identifier of the score.
        :return: The Score object if found, else None.
        """
        return self.scores.get(uid)

    def remove_score(self, uid: str) -> bool:
        """
        Remove a Score by its UID.
        :param uid: Unique identifier of the score.
        :return: True if the score was removed, else False.
        """
        if uid in self.scores:
            del self.scores[uid]
            return True
        return False

    def list_scores(self) -> list:
        """
        List all scores managed by the ScoresManager.
        :return: A list of Score objects.
        """
        return list(self.scores.values())

    def save_all(self):
        """
        Save all scores to individual JSON files named after their UIDs.
        """
        for score in self.scores.values():
            score.save()

    def save(self):
        """
        Save all scores to a single JSON file.
        """
        with open("all_scores.json", "w") as f:
            data = []
            for score in self.scores.values():
                data.append(score.to_json())
            f.write(json.dumps(data))

    def load(self):
        """
        Load scores from a single JSON file.
        """
        try:
            with open("all_scores.json", "r") as f:
                data = json.loads(f.read())
                for score_data in data:
                    score_dict = json.loads(score_data)
                    pdf_data = score_dict["pdf_data"].encode('latin1') if score_dict["pdf_data"] else None
                    score = Score(score_dict["UID"], score_dict["name"], score_dict["has_pdf"], pdf_data)
                    self.scores[score.UID] = score
        except FileNotFoundError:
            pass

