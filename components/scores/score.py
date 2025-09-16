import json


class Score:
    def __init__(self, uid: str, name: str, has_pdf: bool, pdf_data: bytes = None):
        """
        Initialize a Score (notes) object.
        :param name: Name of the score.
        :param has_pdf: Whether the score has an associated PDF.
        :param pdf_data: PDF data as bytes, if available. (Read by PyMuPDF)
        """
        self.UID = uid
        self.name = name
        self.has_pdf = has_pdf
        self.pdf_data = pdf_data

    def to_json(self) -> str:
        """
        Convert the Score object to a JSON string.
        :return: JSON representation of the Score object.
        """
        return json.dumps({
            "UID": self.UID,
            "name": self.name,
            "has_pdf": self.has_pdf,
            "pdf_data": self.pdf_data.decode('latin1') if self.pdf_data else None
        })

    def save(self):
        """
        Save the Score object to a JSON file named after its UID.
        """
        with open(f"{self.UID}.json", "w") as f:
            f.write(self.to_json())
