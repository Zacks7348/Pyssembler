from pathlib import Path

WORK_FOLDER = str(Path('Pyssembler/work').resolve())
GUI = True


def set_gui(val: bool):
    global GUI
    GUI = val


def set_work_folder(val: str):
    global WORK_FOLDER
    WORK_FOLDER = val

