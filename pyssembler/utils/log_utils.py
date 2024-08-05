import logging

__all__ = ['LoggableMixin', 'PyssemblerStreamHandler', 'PrintHandler']

_original_logging_factory = logging.getLogRecordFactory()


class LoggableMixin:
    def get_logger(self, name: str = None, suffix: str = None, level: int = logging.DEBUG):
        if name is None:
            name = self.__class__.__name__
        if suffix is not None:
            name += f'.{suffix}'
        logger = logging.getLogger(f'{self.__class__.__module__}.{name}')
        logger.setLevel(level)
        return logger


class PyssemblerStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Formatting
        fmt = logging.Formatter(
            '[{short_name}] {message}',
            style='{'
        )
        self.setFormatter(fmt)


class PrintHandler(logging.Handler):
    """
    A handler class which prints logging records, appropriately formatted,
    to a stream. Note that this class is a glorified call to print().
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatting
        fmt = logging.Formatter(
            '[{short_name}] {message}',
            style='{'
        )
        self.setFormatter(fmt)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        print(msg)


def _log_record_factory(*args, **kwargs):
    record = _original_logging_factory(*args, **kwargs)
    record.short_name = record.name.split('.')[-1]
    return record


logging.setLogRecordFactory(_log_record_factory)