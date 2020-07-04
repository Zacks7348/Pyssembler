import json

from Pyssembler.environment.helpers import binary

class CPU():
    def __init__(self):
        self.__rf = RegisterFile()
        self.__m = Memory()
        self.__im = IM()
    
    def reg_read(self, address):
        return self.__rf.read(address)
    
    def reg_write(self, data, address):
        self.__rf.write(data, address)

    def ram_read(self, address):
        return self.__m.read(address)
    
    def ram_write(self, data, address):
        self.__m.write(address, data)
    
    @property
    def reg_state(self):
        return self.__rf.registers
    
    @property
    def ram_state(self):
        return self.__m.memory
    
    @property
    def print(self):
        return {"Registers":self.__rf.print,"Memory":self.__m.print}


class States():
    def __init__(self):
        with open("config.json", "r") as in_file:
            self.file = json.load(in_file)
            try:
                self.register_states = self.file["registers"]
            except:
                self.register_states = None
            try:
                self.m_states = self.file["Memory"]
            except:
                self.m_states = None

class RegisterFile():
    def __init__(self):
        with open("Pyssembler/environment/registers.json", "r") as reg_in:
            self.reg_bin = json.load(reg_in)
        self.__registers = {}
        self.__registers[binary(0, 5)] = {"zero": 0}
        self.__registers[binary(1, 5)] = {"$at": 0}
        for i in range(2, 4):
            self.__registers[binary(i, 5)] = {"$v{}".format(i - 2):0}
        for i in range(4, 8):
            self.__registers[binary(i, 5)] = {"$a{}".format(i - 4):0}
        for i in range(8, 16):
            self.__registers[binary(i, 5)] = {"$t{}".format(i - 8):0}
        for i in range(16, 24):
            self.__registers[binary(i, 5)] = {"$s{}".format(i - 16):0}
        for i in range(24, 26):
            self.__registers[binary(i, 5)] = {"$t{}".format(i - 16):0}
        for i in range(26, 28):
            self.__registers[binary(i, 5)] = {"$k{}".format(i - 26):0}
        self.__registers[binary(28, 5)] = {"$gp":0}
        self.__registers[binary(29, 5)] = {"$sp":0}
        self.__registers[binary(30, 5)] = {"$fp":0}
        self.__registers[binary(31, 5)] = {"$ra":0}
        self.__registers['PC'] = {"$pc":0}
        self.__registers['IR'] = {"IR":0}
        
    def read(self, address):
        return self.__registers[address][self.reg_bin[address]]

    def write(self, data, address):
        self.__registers[address][self.reg_bin[address]] = data
    
    @property
    def registers(self):
        return self.__registers
    
    @property
    def print(self):
        output = {}
        for reg in self.__registers.values():
            output[reg.name] = reg.value
        return output

class Memory():
    def __init__(self):
        self.memory = {}
        for i in range(0, 2049, 4):
            self.memory[binary(i, 32)] = 0

    def read(self, address): 
        output = {}
        for key, value in self.memory.items():
            output[int(key)] = value
    
    def write(self, data, address):  
        self.memory[address] = data
    
    @property
    def print(self):
        return self.memory
    
class IM():
    def __init__(self, instructions={}):
        self.instructions = instructions
    
    def read_instruction(self, address):
        return self.instructions[address]
    
    def write_instruction(self, address, instruction):
        self.instructions[address] = instruction