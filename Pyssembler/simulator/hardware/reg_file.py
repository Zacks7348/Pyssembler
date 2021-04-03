import json
import os.path
from typing import Union

from ..utils import MAX_SINT32, MAX_UINT32, MIN_SINT32

REGISTERS = os.path.dirname(__file__)+'/../registers.json'

class RegisterFile:
    """
    Represents a MIPS 32bit RegisterFile

    Creates 2 dicts where each pair of keys point to the same list. This creates the ability
    to access/modify the value of a register either by address or by name. Updating the value
    in one dictionary will also update the value in the other 

    """
    def __init__(self) -> None:
        self.regs = {} # {addr: [value, name]}
        self.regs_name = {}
        with open (REGISTERS, 'r') as f:
            for name, addr in json.load(f)["GPR"].items():
                self.regs[addr] = [0, name]
                self.regs_name[name] = self.regs[addr]
        self.PC = 0
    
    def read(self, addr=None, name=None) -> int:
        """
        Function for reading a value of a register.

        Can either pass address of register or name of register. If name is not None,
        register is accessed by name and anything passed in addr is ignored
        """
        if not addr and not name:
            raise ValueError('Must pass either register address or name')
        if name:
            if name not in self.regs_name:
                raise ValueError('Invalid Register Name')
            return self.regs_name[name][0]
        if not 0 <= addr < 32:
            raise ValueError('Invalid Register Address')
        return self.regs[addr][0]
    
    def write(self, val: int, addr=None, name=None) -> None:
        """
        Function for writing a value to a register

        Can either pass address of register or name of register. If name is not None,
        register is accessed by name and anything passed in addr is ignored
        """
        if not 0 <= val <= MAX_UINT32:
            raise ValueError('Invalid value')
        if not addr and not name:
            raise ValueError('Must pass either register address or name')

        if name:
            if name not in self.regs_name:
                if name == '$PC': self.PC = val
                else: raise ValueError('Invalid Register Name')
            self.regs_name[name][0] = val
            return
        if not 0 <= addr < 32:
            raise ValueError('Invalid GPR Address')
        if addr == 0 or addr == 1:
            return
        self.regs[addr][0] = val
    
    def increment_pc(self):
        self.PC += 4
    
    def get_regs(self):
        return {values[1]:addr for (addr, values) in self.regs.items()}

    def print(self, radix=int):
        formatting = {int: '{}', hex: '0x{:08x}', bin: '{:032b}'}
        for addr, val in self.regs.items():
            print(('{} ({}): '+formatting[radix]).format(addr, val[1], val[0]))
        print(('xxxxx ($PC): '+formatting[radix]).format(self.PC))
        
    def __repr__(self) -> str:
        output = ''
        for addr, val in self.regs.items():
            output += '{} ({}): {}\n'.format(addr, val[1], val[0])
        return output