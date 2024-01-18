from pathlib import Path
from typing import List


class ASMFile:
    def __init__(self, path: Path):
        path = Path(path).resolve()
        if not path.exists():
            raise ValueError(f'ASM file {path} does not exist')
        self.path = Path(path).resolve()
        self._text: str = None
        self._last_modified: int = -1

    def text(self, cache=True):
        last_modified = self.path.stat().st_mtime

        if last_modified > self._last_modified or not cache:
            # Read file from disk
            self._text = self.read()
            self._last_modified = last_modified

        return self._text

    def read(self):
        with self.path.open('r') as f:
            return f.read()

    def __hash__(self):
        return hash(self.path)


class MIPSProgram:
    """
    Represents a MIPS program
    """
    def __init__(self, asm_files: List[Path], exception_handler: Path = None):
        self.asm_files: List[ASMFile] = [ASMFile(asm) for asm in asm_files]
        self.exception_handler: ASMFile = None
        if exception_handler is not None:
            self.exception_handler = ASMFile(exception_handler)
