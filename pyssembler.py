"""
This is the main script of this program.
"""

import logging
# from datetime import datetime

from Pyssembler import run_application


def setup_logging():
    """
    GUI application will use this logging object to log to console
    """
    log = logging.getLogger('Pyssembler')
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # filename = "Pyssembler/logs/pyssembler-{}.log".format(datetime.now().strftime("%y-%m-%d-%M-%S"))
    # handler = logging.FileHandler(filename=filename, encoding='UTF-8', mode='w')
    # handler.setFormatter(formatter)
    # log.addHandler(handler)


def main():
    setup_logging()
    run_application()


if __name__ == '__main__':
    main()
