import logging
from pathlib import Path
from typing import List


class Program:
    """
    Represents a MIPS program
    """
    def __init__(self, asm_files: List[Path], exception_handler: Path):
        self.asm_files: List[Path] = asm_files
        self.exception_handler: Path = exception_handler

        self.statements = []

