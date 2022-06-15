class MemorySize:
    """
    Sizes of supported memory data types
    """
    BIT = 1
    BYTE = 8
    HWORD = 16
    WORD = 32

    BYTE_LENGTH_BYTES = BYTE // BIT
    HWORD_LENGTH_BYTES = HWORD // BYTE
    WORD_LENGTH_BYTES = WORD // BYTE
