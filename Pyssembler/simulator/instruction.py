import os
import json

from .errors import *

class InstructionSet:
    """
    Represents a set of MIPS32 instructions
    """
    def __init__(self, memory, reg_file, coprocessors):
        self.memory = memory
        self.rf = reg_file
        self.coprocessors = coprocessors
        self.instructions = {}
        
    def populate(self):
        """
        Populate the instruction set.

        Instructions store their encodings, formatting, description,
        exceptions, and their op/func/shamt codes
        """
        self.instructions['template'] = {
            'encoding': '',
            'format': 'rd, rs, rt',
            'desc': '',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b00000,
            'shamt': 0b0}

        self.instructions['lb'] = {
            'encoding': '100000{base}{rt}{i16_s}',
            'format': 'lb rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'group': 'CPU Load/Store',
            'op': 0b100000,
            'func': None,
            'shamt': None}

        self.instructions['lbu'] = {
            'encoding': '100100{base}{rt}{i16_s}',
            'format': 'lbu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'group': 'CPU Load/Store',
            'op': 0b100100,
            'func': None,
            'shamt': None}

        self.instructions['lh'] = {
            'encoding': '100001{base}{rt}{i16_s}',
            'format': 'lh rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'group': 'CPU Load/Store',
            'op': 0b100001,
            'func': None,
            'shamt': None}

        self.instructions['lhu'] = {
            'encoding': '100101{base}{rt}{i16_s}',
            'format': 'lhu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'group': 'CPU Load/Store',
            'op': 0b100101,
            'func': None,
            'shamt': None}

        self.instructions['lw'] = {
            'encoding': '100011{base}{rt}{i16_s}',
            'format': 'lw rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'group': 'CPU Load/Store',
            'op': 0b100011,
            'func': None,
            'shamt': None}

        self.instructions['sb'] = {
            'encoding': '101000{base}{rt}{i16_s}',
            'format': 'sb rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'group': 'CPU Load/Store',
            'op': 0b101000,
            'func': None,
            'shamt': None}

        self.instructions['sh'] = {
            'encoding': '101001{base}{rt}{i16_s}',
            'format': 'sh rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'group': 'CPU Load/Store',
            'op': 0b101001,
            'func': None,
            'shamt': None}

        self.instructions['sw'] = {
            'encoding': '101011{base}{rt}{i16_s}',
            'format': 'sw rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'group': 'CPU Load/Store',
            'op': 0b101011,
            'func': None,
            'shamt': None}

        self.instructions['addiu'] = {
            'encoding': '001001{rs}{rt}{i16_s}',
            'format': 'addiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] + sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001001,
            'func': None,
            'shamt': None}
        
        self.instructions['andi'] = {
            'encoding': '001100{rs}{rt}{i16_s}',
            'format': 'andi rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] AND sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001100,
            'func': None,
            'shamt': None}
        
        self.instructions['ori'] = {
            'encoding': '001101{rs}{rt}{i16_s}',
            'format': 'ori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] OR sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001101,
            'func': None,
            'shamt': None}

        self.instructions['slti'] = {
            'encoding': '001010{rs}{rt}{i16_s}',
            'format': 'slti rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001010,
            'func': None,
            'shamt': None}
        
        self.instructions['sltiu'] = {
            'encoding': '001011{rs}{rt}{i16_u}',
            'format': 'sltiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001011,
            'func': None,
            'shamt': None}

        self.instructions['xori'] = {
            'encoding': '001110{rs}{rt}{i16_s}',
            'format': 'xori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] XOR sign_ext(immediate)',
            'group': 'ALU i16',
            'op': 0b001110,
            'func': None,
            'shamt': None}

        self.instructions['add'] = {
            'encoding': '000000{rs}{rt}{rd}00000100000',
            'format': 'add rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100000,
            'shamt': 0b00000}
        
        self.instructions['addu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100001',
            'format': 'addu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100001,
            'shamt': 0b00000}
        
        self.instructions['and'] = {
            'encoding': '000000{rs}{rt}{rd}00000100100',
            'format': 'and rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] AND GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100100,
            'shamt': 0b00000}
        
        self.instructions['nor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100111',
            'format': 'nor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] NOR GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100111,
            'shamt': 0b00000}
        
        self.instructions['or'] = {
            'encoding': '000000{rs}{rt}{rd}00000100101',
            'format': 'or rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] OR GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100101,
            'shamt': 0b00000}
        
        self.instructions['slt'] = {
            'encoding': '000000{rs}{rt}{rd}00000101010',
            'format': 'slt rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b101010,
            'shamt': 0b00000}
        
        self.instructions['sltu'] = {
            'encoding': '000000{rs}{rt}{rd}00000101011',
            'format': 'sltu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b101011,
            'shamt': 0b00000}

        self.instructions['sub'] = {
            'encoding': '000000{rs}{rt}{rd}00000100010',
            'format': 'sub rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100010,
            'shamt': 0b00000}
        
        self.instructions['subu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100011',
            'format': 'subu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b100011,
            'shamt': 0b00000}
        
        self.instructions['xor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100110',
            'format': 'xor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] XOR GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b1,
            'shamt': 0b00000}
        
        self.instructions['mul'] = {
            'encoding': '000000{rs}{rt}{rd}00010011000',
            'format': 'mul rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011000,
            'shamt': 0b00010}
        
        self.instructions['muh'] = {
            'encoding': '000000{rs}{rt}{rd}00011011000',
            'format': 'muh rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011000,
            'shamt': 0b00011}
        
        self.instructions['mulu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011001',
            'format': 'mulu rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011001,
            'shamt': 0b00010}
        
        self.instructions['muhu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011001',
            'format': 'muhu rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011001,
            'shamt': 0b00011}
        
        self.instructions['div'] = {
            'encoding': '000000{rs}{rt}{rd}00010011010',
            'format': 'div rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011010,
            'shamt': 0b00010}
        
        self.instructions['mod'] = {
            'encoding': '000000{rs}{rt}{rd}00011011010',
            'format': 'mod rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011010,
            'shamt': 0b00011}
        
        self.instructions['divu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011011',
            'format': 'divu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011011,
            'shamt': 0b00010}
        
        self.instructions['modu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011011',
            'format': 'modu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'group': 'ALU 3-Op',
            'op': 0b000000,
            'func': 0b011011,
            'shamt': 0b00011}

        self.instructions['clo'] = {
            'encoding': '000000{rs}00000{rd}00001010001',
            'format': 'clo rd, rs',
            'desc': 'GPR[rd] = count_leading_ones(GPR[rs])',
            'group': 'ALU 2-Op',
            'op': 0b000000,
            'func': 0b010001,
            'shamt': 0b00001}
        
        self.instructions['clz'] = {
            'encoding': '000000{rs}00000{rd}00001010000',
            'format': 'clz rd, rs',
            'desc': 'GPR[rd] = count_leading_zeroes(GPR[rs])',
            'group': 'ALU 2-Op',
            'op': 0b000000,
            'func': 0b010000,
            'shamt': 0b00001}






















































































































