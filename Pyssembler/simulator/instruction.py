class Instruction:
    def __init__(self, instr: str) -> None:
        if len(instr) != 32:
            raise ValueError('Invalid machine code! Must be 32 bit binary str')
        self.bits = instr
        self.op = self.bits[:6]
        self.reg1 = self.bits[6:11]
        self.reg2 = self.bits[11:15]
        self.reg3 = self.bits[15:19]
        self.i = self.bits[15:]
        self.j = self.bits[6:]
        self.func = self.bits[26:]
    
    def __repr__(self):
        return 'Instruction: '+self.bits
