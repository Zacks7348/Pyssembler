def __init_logging():
    import logging

    # Initialize logging
    logging.getLogger(__name__).addHandler(logging.NullHandler())

    # For debugging purposes
    logging.basicConfig(level=logging.DEBUG)


__init_logging()
