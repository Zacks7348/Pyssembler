from Pyssembler.errors import PyssemblerException

class MemoryError(PyssemblerException):
    """
    This exception is thrown when an error occurs during
    a memory operation

    This inherits from :class:`PyssemblerException`
    """
    def __init__(self, message='An error occured during a memory operation'):
        error_message = 'An error occured during a memory operation\n\t {message}'
        super().__init__(error_message.format(message=message))