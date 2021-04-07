import os
import json
from enum import Enum

from .errors import *

class InstructionType(Enum):
    
    R_TYPE = 0
    I_TYPE = 1 
    I_B_TYPE = 2
    J_TYPE = 3

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

        self.instructions['lb'] = {
            'encoding': '100000{base}{rt}{i16_s}',
            'format': 'lb rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'op': 0b100000,
            'func': None,
            'unique': None}

        self.instructions['lbu'] = {
            'encoding': '100100{base}{rt}{i16_s}',
            'format': 'lbu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'op': 0b100100,
            'func': None,
            'unique': None}

        self.instructions['lh'] = {
            'encoding': '100001{base}{rt}{i16_s}',
            'format': 'lh rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'op': 0b100001,
            'func': None,
            'unique': None}

        self.instructions['lhu'] = {
            'encoding': '100101{base}{rt}{i16_s}',
            'format': 'lhu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'op': 0b100101,
            'func': None,
            'unique': None}

        self.instructions['lw'] = {
            'encoding': '100011{base}{rt}{i16_s}',
            'format': 'lw rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'op': 0b100011,
            'func': None,
            'unique': None}

        self.instructions['sb'] = {
            'encoding': '101000{base}{rt}{i16_s}',
            'format': 'sb rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'op': 0b101000,
            'func': None,
            'unique': None}

        self.instructions['sh'] = {
            'encoding': '101001{base}{rt}{i16_s}',
            'format': 'sh rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'op': 0b101001,
            'func': None,
            'unique': None}

        self.instructions['sw'] = {
            'encoding': '101011{base}{rt}{i16_s}',
            'format': 'sw rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'op': 0b101011,
            'func': None,
            'unique': None}

        self.instructions['addiu'] = {
            'encoding': '001001{rs}{rt}{i16_s}',
            'format': 'addiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] + sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001001,
            'func': None,
            'unique': None}
        
        self.instructions['andi'] = {
            'encoding': '001100{rs}{rt}{i16_s}',
            'format': 'andi rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] AND sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001100,
            'func': None,
            'unique': None}
        
        self.instructions['ori'] = {
            'encoding': '001101{rs}{rt}{i16_s}',
            'format': 'ori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] OR sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001101,
            'func': None,
            'unique': None}

        self.instructions['slti'] = {
            'encoding': '001010{rs}{rt}{i16_s}',
            'format': 'slti rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001010,
            'func': None,
            'unique': None}
        
        self.instructions['sltiu'] = {
            'encoding': '001011{rs}{rt}{i16_u}',
            'format': 'sltiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001011,
            'func': None,
            'unique': None}

        self.instructions['xori'] = {
            'encoding': '001110{rs}{rt}{i16_s}',
            'format': 'xori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] XOR sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'op': 0b001110,
            'func': None,
            'unique': None}

        self.instructions['add'] = {
            'encoding': '000000{rs}{rt}{rd}00000100000',
            'format': 'add rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100000,
            'unique': None}
        
        self.instructions['addu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100001',
            'format': 'addu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100001,
            'unique': None}
        
        self.instructions['and'] = {
            'encoding': '000000{rs}{rt}{rd}00000100100',
            'format': 'and rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] AND GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100100,
            'unique': None}
        
        self.instructions['nor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100111',
            'format': 'nor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] NOR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100111,
            'unique': None}
        
        self.instructions['or'] = {
            'encoding': '000000{rs}{rt}{rd}00000100101',
            'format': 'or rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] OR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100101,
            'unique': None}
        
        self.instructions['slt'] = {
            'encoding': '000000{rs}{rt}{rd}00000101010',
            'format': 'slt rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b101010,
            'unique': None}
        
        self.instructions['sltu'] = {
            'encoding': '000000{rs}{rt}{rd}00000101011',
            'format': 'sltu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b101011,
            'unique': None}

        self.instructions['sub'] = {
            'encoding': '000000{rs}{rt}{rd}00000100010',
            'format': 'sub rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100010,
            'unique': None}
        
        self.instructions['subu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100011',
            'format': 'subu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b100011,
            'unique': None}
        
        self.instructions['xor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100110',
            'format': 'xor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] XOR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b1,
            'unique': None}
        
        self.instructions['mul'] = {
            'encoding': '000000{rs}{rt}{rd}00010011000',
            'format': 'mul rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011000,
            'unique': (0x000007C0, 0b00010)}
        
        self.instructions['muh'] = {
            'encoding': '000000{rs}{rt}{rd}00011011000',
            'format': 'muh rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011000,
            'unique': (0x000007C0, 0b00011)}
        
        self.instructions['mulu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011001',
            'format': 'mulu rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011001,
            'unique': (0x000007C0, 0b00010)}
        
        self.instructions['muhu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011001',
            'format': 'muhu rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011001,
            'unique': (0x000007C0, 0b00011)}
        
        self.instructions['div'] = {
            'encoding': '000000{rs}{rt}{rd}00010011010',
            'format': 'div rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011010,
            'unique': (0x000007C0, 0b00010)}
        
        self.instructions['mod'] = {
            'encoding': '000000{rs}{rt}{rd}00011011010',
            'format': 'mod rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011010,
            'unique': (0x000007C0, 0b00011)}
        
        self.instructions['divu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011011',
            'format': 'divu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011011,
            'unique': (0x000007C0, 0b00010)}
        
        self.instructions['modu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011011',
            'format': 'modu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b011011,
            'unique': (0x000007C0, 0b00011)}

        self.instructions['clo'] = {
            'encoding': '000000{rs}00000{rd}00001010001',
            'format': 'clo rd, rs',
            'desc': 'GPR[rd] = count_leading_ones(GPR[rs])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b010001,
            'unique': None}
        
        self.instructions['clz'] = {
            'encoding': '000000{rs}00000{rd}00001010000',
            'format': 'clz rd, rs',
            'desc': 'GPR[rd] = count_leading_zeroes(GPR[rs])',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b010000,
            'unique': None}

        self.instructions['sll'] = {
            'encoding': '00000000000{rt}{rd}{sa}000000',
            'format': 'sll rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] << sa',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000000,
            'unique': None}

        self.instructions['sra'] = {
            'encoding': '00000000000{rt}{rd}{sa}000011',
            'format': 'sra rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] >> sa',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000011,
            'unique': None}    

        self.instructions['srl'] = {
            'encoding': '00000000000{rt}{rd}{sa}000010',
            'format': 'srl rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] >> sa',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000010,
            'unique': None}

        self.instructions['sllv'] = {
            'encoding': '000000{rs}{rt}{rd}00000000100',
            'format': 'sllv rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] << GPR[rs]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000100,
            'unique': None}
        
        self.instructions['srav'] = {
            'encoding': '000000{rs}{rt}{rd}00000000111',
            'format': 'srav rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] >> GPR[rs]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000111,
            'unique': None}

        self.instructions['srlv'] = {
            'encoding': '000000{rs}{rt}{rd}00000000110',
            'format': 'srlv rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] >> GPR[rs]',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000110,
            'unique': None}

        self.instructions['j'] = {
            'encoding': '000010{i26_u}',
            'format': 'j target',
            'desc': 'set PC = target',
            'type': InstructionType.J_TYPE,
            'op': 0b000010,
            'func': None,
            'unique': None}
        
        self.instructions['jal'] = {
            'encoding': '000011{i26_u}',
            'format': 'jal target',
            'desc': 'set PC = target and link',
            'type': InstructionType.J_TYPE,
            'op': 0b000011,
            'func': None,
            'unique': None}

        self.instructions['jalr'] = {
            'encoding': '000000{rs}00000{rd}00000001001',
            'format': 'jalr rs',
            'desc': 'GPR[31] = return_addr, PC = GPR[rs]',
            'type': InstructionType.R_TYPE,
            'op': 0b000010,
            'func': None,
            'unique': None}
        
        self.instructions['jic'] = {
            'encoding': '11011000000{rt}{i16_s}',
            'format': 'jic rt, offset',
            'desc': 'PC = GPR[rt] + sign_extend(offset)',
            'group': 'Indexed Jumps',
            'op': 0b110110,
            'func': None,
            'unique': None}

        self.instructions['jialc'] = {
            'encoding': '11111000000{rt}{i16_s}',
            'format': 'jialc rt, offset',
            'desc': 'GPR[31] = PC+4, PC = GPR[rt] + sign_extend(offset)',
            'type': InstructionType.J_TYPE,
            'op': 0b111110,
            'func': None,
            'unique': None}

        self.instructions['bc'] = {
            'encoding': '110010{i26_s}',
            'format': 'bc offset',
            'desc': 'PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b110010,
            'func': None,
            'unique': None}

        self.instructions['balc'] = {
            'encoding': '111010{i26_s}',
            'format': 'balc offset',
            'desc': 'GPR[31] = PC+4, PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b111010,
            'func': None,
            'unique': None}

        self.instructions['beqzc'] = {
            'encoding': '110110{rs}{i21_s}',
            'format': 'beqzc rs, offset',
            'desc': 'if GPR[rs] == 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b110110,
            'func': None,
            'unique': None}

        self.instructions['bnezc'] = {
            'encoding': '111110{rs}{i21_s}',
            'format': 'bnezc rs, offset',
            'desc': 'if GPR[rs] != 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b111110,
            'func': None,
            'unique': None}

        self.instructions['blezc'] = {
            'encoding': '01011000000{rt}{i16_s}',
            'format': 'blezc rt, offset',
            'desc': 'if GPR[rt] < 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b010110,
            'func': None,
            'unique': None}

        self.instructions['bgtzc'] = {
            'encoding': '01011100000{rt}{i16_s}',
            'format': 'bgtzc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b010111,
            'func': None,
            'unique': None}

        self.instructions['beqzalc'] = {
            'encoding': '00100000000{rt}{i16_s}',
            'format': 'beqzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b010000,
            'func': None,
            'unique': None}
        
        self.instructions['bnezalc'] = {
            'encoding': '01100000000{rt}{i16_s}',
            'format': 'bnezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b011000,
            'func': None,
            'unique': None}
        
        self.instructions['blezalc'] = {
            'encoding': '00011000000{rt}{i16_s}',
            'format': 'blezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bgtzalc'] = {
            'encoding': '00011100000{rt}{i16_s}',
            'format': 'bgtzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['bgezc'] = {
            'encoding': '010110{rt}{rt}{i16_s}',
            'format': 'bgezc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b010110,
            'func': None,
            'unique': None}

        self.instructions['bltzc'] = {
            'encoding': '010111{rt}{rt}{i16_s}',
            'format': 'bltzc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b010111,
            'func': None,
            'unique': None}

        self.instructions['bgezalc'] = {
            'encoding': '000110{rt}{rt}{i16_s}',
            'format': 'bgezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bltzalc'] = {
            'encoding': '000111{rt}{rt}{i16_s}',
            'format': 'bltzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['beq'] = {
            'encoding': '000100{rs}{rt}{i16_s}',
            'format': 'beq rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000100,
            'func': None,
            'unique': None}

        self.instructions['bne'] = {
            'encoding': '000101{rs}{rt}{i16_s}',
            'format': 'bne rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000101,
            'func': None,
            'unique': None}

        self.instructions['bgeuc'] = {
            'encoding': '000110{rs}{rt}{i16_s}',
            'format': 'bgeuc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bltuc'] = {
            'encoding': '000111{rs}{rt}{i16_s}',
            'format': 'bltuc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['bovc'] = {
            'encoding': '001000{rs}{rt}{i16_s}',
            'format': 'bovc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b001000,
            'func': None,
            'unique': None}

        self.instructions['bnvc'] = {
            'encoding': '011000{rs}{rt}{i16_s}',
            'format': 'bnvc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b011000,
            'func': None,
            'unique': None}
        
        self.instructions['bnvc'] = {
            'encoding': '011000{rs}{rt}{i16_s}',
            'format': 'bnvc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b011000,
            'func': None,
            'unique': None}
        
        self.instructions['bnvc'] = {
            'encoding': '011000{rs}{rt}{i16_s}',
            'format': 'bnvc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'op': 0b011000,
            'func': None,
            'unique': None}

        self.instructions['mfc0'] = {
            'encoding': '01000000000{rt}{rd}00000000000',
            'format': 'mfc0 rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'op': 0b010000,
            'func': 0b000000,
            'unique': (0x03E00000, 0b00000)}

        self.instructions['mtc0'] = {
            'encoding': '01000000100{rt}{rd}00000000000',
            'format': 'mtc0 rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'op': 0b010000,
            'func': 0b000000,
            'unique': (0x03E00000, 0b00100)}

        self.instructions['syscall'] = {
            'encoding': '00000000000000000000000000001100',
            'format': 'syscall',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b001100,
            'unique': None}

        self.instructions['break'] = {
            'encoding': '00000000000000000000000000001101',
            'format': 'break',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b001101,
            'unique': None}

        self.instructions['nop'] = {
            'encoding': '00000000000000000000000000000000',
            'format': 'break',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'op': 0b000000,
            'func': 0b000000,
            'unique': None} 
























































