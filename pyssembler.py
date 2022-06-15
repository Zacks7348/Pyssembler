"""
main script of the Pyssembler project
"""
import logging

from pyssembler.gui import run


__LOGGER__ = logging.getLogger(__name__)


def main():
    __LOGGER__.debug('Running...')
    run()


if __name__ == '__main__':
    main()
