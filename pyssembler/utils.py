import logging


class LoggableMixin:
    def get_logger(self, name: str = None, suffix: str = None):
        if name is None:
            name = self.__class__.__name__
        if suffix is not None:
            name += f'.{suffix}'
        return logging.getLogger(f'{self.__class__.__module__}.{name}')
