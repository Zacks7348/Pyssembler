import logging

__all__ = ['PYSSEMBLER_ROOT_LOGGER']


PYSSEMBLER_ROOT_LOGGER = logging.getLogger(__name__)


def __init_logging():
    # Initialize logging
    PYSSEMBLER_ROOT_LOGGER.addHandler(logging.NullHandler())


__init_logging()
