import logging

# Configure logging
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)
_fmt = logging.Formatter(fmt='[{name}][{levelname}] {message}', style='{')

_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
_log.addHandler(_sh)