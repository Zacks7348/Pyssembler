from enum import IntEnum


class MIPSMemorySize(IntEnum):
    BIT = 1
    BYTE = 8
    HWORD = 16
    WORD = 32
    DWORD = 64

    BYTE_LENGTH_BYTES = BYTE // BYTE
    HWORD_LENGTH_BYTES = HWORD // BYTE
    WORD_LENGTH_BYTES = WORD // BYTE
    DWORD_LENGTH_BYTES = DWORD // BYTE
