from typing import List

class PyssemblerProject:
    """
    Represents a Pyssembler Project
    """

    def __init__(self, files: List[str] = None) -> None:
        self.files = files if files else []
        self.main_file = None
        