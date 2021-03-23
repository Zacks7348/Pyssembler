MAX_UINT32 = 0xffffffff
MAX_SINT32 = 0x7fffffff
MIN_SINT32 = -0x80000000

class ALU:
    """
    Represents a 32 bit Arithmetic Logic Unit

    Given two inputs (a and b) and a opcode, returns result of
    arithmetic

    All Calculations are done on binary strings to better show process
    """
    def run(self, a: int, b: int, op: str) -> int:
        result = 0
        overflow = False
        if op == '000': result = a & b
        if op == '001': result = a | b
        if op == '010': result = a + b
        if op == '011': result = a - b
        if op == '100': result = a * b
        if op == '101': result = a / b
        if op == '110': result = a < b
        if result > MAX_UINT32: 
            overflow = True
            result = MAX_UINT32 % result

        return result, overflow

alu = ALU()
print(alu.run(MAX_UINT32, MAX_UINT32, '010'))