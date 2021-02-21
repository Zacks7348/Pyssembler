import json

from Pyssembler.environment.helpers import binary


class CPU:
    def __init__(self):
        self.reg_file = RegisterFile()
        self.PC = binary(0, 32)
        self.HI = binary(0, 32)
        self.LO = binary(0, 32)
    
    @property
    def registers(self):
        output = self.reg_file.registers
        output.append(('$pc', self.PC))
        output.append(('$hi', self.HI))
        output.append(('$lo', self.LO))
        return output

class RegisterFile:
    def __init__(self):
        self.register_list = {}
        with open('Pyssembler/lib/language/registers.json') as reg_list:
            regs = json.load(reg_list)
            for address, reg in regs.items():
                self.register_list[address] = (binary(0, 32), reg)
    
    @property
    def registers(self):
        output = []
        for reg in self.register_list.values():
            output.append((reg[1], reg[0]))
        return output

class Memory:
    pass


class IM:
    def __init__(self, instructions={}):
        self.instructions = instructions

    def read_instruction(self, address):
        return self.instructions[address]

    def write_instruction(self, address, instruction):
        self.instructions[address] = instruction
