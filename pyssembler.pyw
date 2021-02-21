import logging

from Pyssembler import run

log = logging.getLogger("Pyssembler")
log.setLevel(logging.CRITICAL)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)
debug = True

if __name__ == '__main__':
    run()
          