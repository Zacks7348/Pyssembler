MAX_UINT32 = 0xffffffff
MAX_SINT32 = 0x7fffffff
MIN_SINT32 = -0x80000000

WORD = 32
HWORD = 16
BYTE = 8
BIT = 1

def int2bin(n: int, bits=32, signed=False) -> str:
    """
    Utility function for representing an integer as a 32 bit binary string

    Allows for signed and unsigned representations 
    """
    if bits > 32:
        raise ValueError('int2bin only supports up to 32 bits!')

    if n > MAX_UINT32:
        raise ValueError('int n too big for unsigned 32 bit representation')

    if not signed:
        if n < 0:
            raise ValueError('Cannot represent negative int as unsigned!')
        return f'{n:032b}'[:bits]

    if not MIN_SINT32 <= n <= MAX_SINT32:
        raise ValueError('int n too big/small for signed 32 bit representation ')

    b = '{:032b}'.format(n & MAX_UINT32)
    return b[:bits]       

def bin2int(b: str, signed=False) -> int:
    """
    Utility function for representing a 32 bit binary string as an int

    Allows for signed and unsigned conversions
    """
    if not signed:
        return int(b, 2)
    if b[0] == '0':
        return int(b, 2)
    return (MAX_UINT32 - int(b, 2) + 1)*-1 

def sign_extend(b: str, bits=32) -> str:
    """
    Utility function for sign extending a binary string
    """
    result = b
    while len(result) < bits:
        result = result[0]+result
    return result

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
    output = []
    to_add = ''
    for line in code:
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
        output.append(' '.join(to_add.split()))
        #print('[CC] Added "{}" to output'.format(to_add))
        to_add = ''
    return output


if __name__ == '__main__':
    n = -2048
    x = int2bin(n, signed=True)
    print(n, x, len(x), bin2int(x, signed=True))
