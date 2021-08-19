# Global config settings
DEBUG = False
GUI = False
LOG_FILE = None

def set_debug(debug: bool) -> None:
    global DEBUG
    DEBUG = debug

def set_gui(gui: bool) -> None:
    global GUI
    GUI = gui

def set_log_file(outfile: str) -> None:
    global LOG_FILE
    LOG_FILE = outfile