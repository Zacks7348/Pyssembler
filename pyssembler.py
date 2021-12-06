"""
This is the main script of this program. Running Pyssembler
with this file will also include a console. For just a GUI run 
the program with pyssembler.pyw
"""

import logging

from Pyssembler import run_application

def setup_logging():
    """
    GUI application will use this logging object to log to console
    """
    log = logging.getLogger('Pyssembler')
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(name)s][%(levelname)s] %(message)s'))
    log.addHandler(handler)

def main():
    setup_logging()
    run_application()

if __name__ == '__main__':
    main()