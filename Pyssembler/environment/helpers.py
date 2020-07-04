import os, json

def binary(n, bits: int):
    output = ""
    n = int(n)
    negative = False
    if n < 0:
        negative = True
        n *= -1
    if bits == 5:
        output = f'{n:05b}'
    elif bits == 16:
        output = f'{n:016b}'
    elif bits == 26:
        output = f'{n:026b}'
    elif bits == 32:
        output = f'{n:032b}'
    if negative:
        output = binary(integer(invert(output))+1, bits)
    return output

def integer(b, complement=False):
    if complement:
        if b[0] == "1":
            tmp = invert(binary(integer(b)-1, len(b)))
            return int('0b'+tmp, 2)*-1
    return int('0b'+b, 2)

def invert(binary):
    output = ""
    for b in binary:
        if b == "0":
            output += "1"
        else:
            output += "0"
    return output

def clean_code(code):
    output = []
    for line in code:
        if line == '':
            continue
        if not line.startswith("#"):
            if "#" in line:
                output.append(line.split("#", 1)[0].lstrip(' '))
            elif not line.isspace():
                output.append(line.lstrip(' '))
    return output
