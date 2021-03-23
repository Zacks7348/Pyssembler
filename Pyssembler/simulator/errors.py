class TranslationError(Exception):
    """
    The base exception type for all translation related errors

    This inherits from :class:`Exception`

    """

    def __init__(self, line=None, line_num=None):
        self.line = line
        self.line_num = line_num

    def __str__(self):
        return "TranslationError: Could not translate {} on line {}".format(
            self.line, self.line_num
        )


class InvalidBinaryInstructionError(TranslationError):
    """
    The base exception type for all binary instruction specific exceptions

    This inherits from :class:`TranslationError`
    """

    def __str__(self):
        return "InvalidBinaryInstructionError: Could not translate binary instruction {} on line {}".format(
            self.line, self.line_num
        )


class InvalidSizeError(InvalidBinaryInstructionError):
    """
    Exception raised when binary instruction is not 32

    This inherits from :class:`InvalidBinaryInstructionError`
    """

    def __str__(self):
        return "InvalidInstructionSizeError: Binary Instruction is not 32 bits on line {}".format(
            self.line_num
        )


class InvalidOperationError(InvalidBinaryInstructionError):
    """
    Exception raised when a binary instruction has an unknown op-code

    This inherits from :class:`InvalidBinaryInstructionError`
    """

    def __init__(self, line, line_num, code):
        super().__init__(line, line_num)
        self.code = code

    def __str__(self):
        return "InvalidOperationError: Unsupported instruction with op-code {} on line {}".format(
            self.code, self.line_num
        )


class InvalidFunctionError(InvalidBinaryInstructionError):
    """
    Exception raised when a binary instruction has an unknown func-code

    This inherits from :class:`InvalidBinaryInstructionError`
    """

    def __init__(self, line, line_num, code):
        super().__init__(line, line_num)
        self.code = code

    def __str__(self):
        return "InvalidFunctionError: Unsupported instruction with func-code {} on line {}".format(
            self.code, self.line_num
        )


class InvalidTargetError(InvalidBinaryInstructionError):
    """
    Exception raised when a binary instruction has an invalid target

    This inherits from :class:`InvalidBinaryInstructionError`
    """

    def __init__(self, line, line_num, target):
        super().__init__(line, line_num)
        self.target = target

    def __str__(self):
        return "InvalidTargetError: Invalid jump target to {} from line {}".format(
            self.target, self.line_num
        )


class InvalidOffsetError(InvalidBinaryInstructionError):
    """
    Exception raised when a binary instruction has an invalid offset

    This inherits from :class:`InvalidBinaryInstructionError`
    """

    def __init__(self, line, line_num, offset):
        super().__init__(line, line_num)
        self.offset = offset

    def __str__(self):
        return "InvalidOffsetError: Invalid branch offset {} from line {}".format(
            self.offset, self.line_num
        )


class InvalidMIPSInstructionError(TranslationError):
    """
    The base exception type for all MIPS instruction exceptions

    This inherits from :class:`TranslationError`
    """

    def __str__(self):
        return "InvalidMIPSInstructionError({}): Could not translate MIPS instruction {}".format(
            self.line_num, self.line
        )


class InvalidInstructionError(InvalidMIPSInstructionError):
    """
    Exception raised when a MIPS instruction has an invalid operation

    This inherits from :class:`InvalidMIPSInstructionError`
    """

    def __init__(self, line, line_num, operation):
        super().__init__(line, line_num)
        self.op = operation

    def __str__(self):
        return "InvalidRegisterError({}): Invalid operation {}".format(
            self.line_num, self.op
        )


class InvalidRegisterError(InvalidMIPSInstructionError):
    """
    Exception raised when a MIPS instruction has an invalid register

    This inherits from :class:`InvalidMIPSInstructionError`
    """

    def __init__(self, line, line_num, register):
        super().__init__(line, line_num)
        self.register = register

    def __str__(self):
        return "InvalidRegisterError({}): Invalid register {}".format(
            self.line_num, self.register
        )


class InvalidLabelError(InvalidMIPSInstructionError):
    """
    Exception raised when a MIPS instruction has an invalid label

    This inherits from :class:`InvalidMIPSInstructionError`
    """

    def __init__(self, line, line_num, label):
        super().__init__(line, line_num)
        self.label = label

    def __str__(self):
        return "InvalidLabelError({}): Invalid label {}".format(
            self.line_num, self.label
        )