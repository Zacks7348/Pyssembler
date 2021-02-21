import logging
from datetime import datetime
from tkinter import constants

from Pyssembler import run

log = logging.getLogger("Pyssembler")
log.setLevel(logging.DEBUG)
filename = "Pyssembler/logs/pyssembler-{}.log".format(datetime.now().strftime("%y-%m-%d-%M-%S"))
handler = logging.FileHandler(filename=filename, encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)

console = False
if console:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s: %(message)s"))
    log.addHandler(handler)

if __name__ == "__main__":
    run()
