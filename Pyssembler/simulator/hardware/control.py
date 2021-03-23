class Control:
    """
    Represents MIPS32 Single Cycle CPU Controller

    Signal Table follows the following format:
    {Opcode: (RegDst, RegWrite, ALUSrc, ALUOp, MemWrite, MemRead, MemToReg,)}

    Opcode 000000 points to a sub signal table with funccodes
    """
    def __init__(self) -> None:
        self.R_OP = '000000'
        self.signal_table = {
            self.R_OP: { # R types
                '100000': (1, 1, 0, '010', 0, 0, 0), # add
                '100100': (1, 1, 0, '000', 0, 0, 0), # and
                '100101': (1, 1, 0, '001', 0, 0, 0), # or
                '100010': (1, 1, 0, '110', 0, 0, 0), # sub
                '101010': (1, 1, 0, '111', 0, 0, 0)  # slt
            },
            '100011': (0, 1, 1, '010', 0, 1, 1), # lw
            '101011': (0, 0, 1, '010', 1, 0, 0), # sw
            '000100': (0, 0, 0, '110', 0, 0, 0)
        }
    
    def get_signals(self, op: str, func: str) -> tuple:
        if op not in self.signal_table:
            raise ValueError('Invalid op code')
        if op == self.R_OP:
            if func not in self.signal_table[self.R_OP]:
                raise ValueError('Invalid func code')
            return self.signal_table[op][func]
        return self.signal_table[op]