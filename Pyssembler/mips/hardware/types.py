class DataType:
    """
    Stores some usefull integer max/min values
    """
    MAX_UINT32 = 0xFFFFFFFF
    MAX_SINT32 = 0x7FFFFFFF
    MIN_SINT32 = -0x80000000

    MAX_UINT16 = 0XFFFF
    MAX_SINT16 = 0x7FFF
    MIN_SINT16 = -0x8000

    MAX_UINT8 = 0xFF
    MAX_SINT8 = 0x7F
    MIN_SINT8 = -0x80

class MemorySize:
    """
    Stores some useful memory size values
    """
    BIT = 1
    BYTE = 8
    HWORD = 16
    WORD = 32
    WORD_LENGTH_BYTES = WORD // BYTE
    HWORD_LENGTH_BYTES = HWORD // BYTE
    BYTE_LENGTH_BYTES = BYTE // BYTE