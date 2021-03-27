from typing import Union

MAX_UINT32 = 0xffffffff
MAX_SINT32 = 0x7fffffff
MIN_SINT32 = -0x80000000

DWORD = 64
WORD = 32
HWORD = 16
BYTE = 8
BIT = 1

def sign_extend(b: str, bits=32) -> str:
    """
    Utility function for sign extending a binary string
    """
    result = b
    while len(result) < bits:
        result = result[0]+result
    return result

def zero_extend(b: str, bits) -> str:
    """
    Utility function for zer-extending binary string
    """
    if bits < len(b):
        raise ValueError('Cannot zero-extend binary string to shorter bit length')
    while len(b) < bits: b = '0' + b
    return b

def clean_code_old(code: list):
    output = []
    to_add = ""
    for line in code:
        line = line.strip()
        if line.startswith('#'):
            continue
        if line.endswith(":"):
            to_add = line + " "
            continue
        if line == "":
            continue
        if "#" in line:
            to_add += line.split("#", 1)[0]
        else:
            to_add += line
        if to_add: output.append(to_add)
        to_add = ""
    return output

def clean_code(code: list) -> list:
    output = [] # list of tuples (line, original line number)
    to_add = ''
    for i, line in enumerate(code):
        line = line.strip()
        #print('[CC] line="{}", to_add="{}"'.format(line, to_add))
        if line.startswith('#') or line == '':
            continue
        if '#' in line:
            line = line.split('#', 1)[0].strip()
        if line.endswith(":"):
            to_add = line + " "
            continue
        to_add += line
        output.append((' '.join(to_add.split()), i+1))
        #print('[CC] Added "{}" to output'.format(to_add))
        to_add = ''
    return output


class Integer:
    """
    Utility class that provides functions for translating
    datatypes into ints
    """
    @staticmethod
    def from_binary(b: str, signed=False) -> int:
        """
        Converts both signed and unsigned binary strings into
        ints
        """
        if len(str) > 32 or len(str) == 0:
            raise ValueError('Cannot convert binary string to int:' \
                'binary string must have [0, 32] bits')
        # if unsigned or signed and positive
        if not signed or b[0] == '0': return int(b, 2)
        return (MAX_UINT32 - int(b, 2) + 1)*-1

class Binary:
    """
    Utility class that provides functions for translating
    datatypes into binary strings
    """
    @staticmethod
    def from_int(i: Union[int, str], bits=32, signed=False) -> str:
        """
        Converts ints into signed and unsigned binary strings
        """
        i = int(i)
        if not 0 < bits <= 32:
            raise ValueError('Cannot convert int to binary string:' \
                'bit count must be in range [1, 32]')
        if not signed:
            if not 0 <= i <= MAX_UINT32: 
                raise ValueError('Cannot convert int to unsigned binary string:' \
                    ' Must be in range [0, {}]'.format(MAX_UINT32))
            return f'{i:032b}'[32-bits:]
        if not MIN_SINT32 <= i <= MAX_SINT32:
            raise ValueError('Cannot convert int to signed binary string: ' \
                'Must be in range [{}, {}]'.format(MIN_SINT32, MAX_SINT32))
        return '{:032b}'.format(i & MAX_UINT32)[32-bits:]   

if __name__ == '__main__':
    print(Binary.from_int(-16, signed=True))

