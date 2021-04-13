from enum import Enum

from .mips_exceptions import *


class InstructionType(Enum):

    R_TYPE = 0
    I_TYPE = 1
    I_B_TYPE = 2
    J_TYPE = 3


class InstructionSet:
    """
    Represents a set of MIPS32 instructions
    """

    def __init__(self):
        self.instructions = {}
        self.OP_MASK = (0xFC000000, 26)
        self.FUNC_MASK = 0x0000003F
        self.REG1_MASK = (0x03E00000, 21)
        self.REG2_MASK = (0x001F0000, 16)
        self.REG3_MASK = (0x0000F800, 11)
        self.I16_MASK = 0x0000FFFF

    def best_match(self, instr: int):
        """
        Tries to match a binary instruction with 
        a mnemonic 
        """
        best_match = None
        best_match_num = 0
        instr_op = (instr & self.OP_MASK) >> 26
        instr_func = instr & self.FUNC_MASK
        for name, info in self.instructions.items():
            match_num = 0
            if info['op'] == instr_op:
                match_num += 1
                if info['func'] == instr_func:
                    match_num += 1
                    if info['unique']:
                        if info['unique'][1] == (instr & info['unique'][0]) >> info['unique'][2]:
                            match_num += 1
            if match_num > best_match_num:
                best_match = name
                best_match_num = match_num
        return best_match

    def get_info(self, instr):
        return self.instructions.get(instr, None)

    def populate(self):
        """
        Populate the instruction set.

        Instructions store their encodings, formatting, description,
        exceptions, and their identifiers

        Instr: {
            encoding: binary encoding
            format: formatting of assembly representation
            desc: description of instruction
            type: instruction formatting type
            op: opcode (bits 31-26)
            func: func code (bits 5-0), None if instr does not use func code
            unique: (mask, value) of specific indentity bits of an instr that aren't op or func
        }
        TODO: descriptions for all instructions
        """

        self.instructions['lb'] = {
            'encoding': '100000{base}{rt}{offset}',
            'format': 'lb rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b100000,
            'func': None,
            'unique': None}

        self.instructions['lbu'] = {
            'encoding': '100100{base}{rt}{offset}',
            'format': 'lbu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b100100,
            'func': None,
            'unique': None}

        self.instructions['lh'] = {
            'encoding': '100001{base}{rt}{offset}',
            'format': 'lh rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b100001,
            'func': None,
            'unique': None}

        self.instructions['lhu'] = {
            'encoding': '100101{base}{rt}{offset}',
            'format': 'lhu rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b100101,
            'func': None,
            'unique': None}

        self.instructions['lw'] = {
            'encoding': '100011{base}{rt}{offset}',
            'format': 'lw rt, offset(base)',
            'desc': 'GPR[rt] = memory[GPR[base] + offset]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b100011,
            'func': None,
            'unique': None}

        self.instructions['sb'] = {
            'encoding': '101000{base}{rt}{offset}',
            'format': 'sb rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b101000,
            'func': None,
            'unique': None}

        self.instructions['sh'] = {
            'encoding': '101001{base}{rt}{offset}',
            'format': 'sh rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b101001,
            'func': None,
            'unique': None}

        self.instructions['sw'] = {
            'encoding': '101011{base}{rt}{offset}',
            'format': 'sw rt, offset(base)',
            'desc': 'memory[GPR[base] + offset] = GPR[rt]',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b101011,
            'func': None,
            'unique': None}

        self.instructions['addiu'] = {
            'encoding': '001001{rs}{rt}{immediate}',
            'format': 'addiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] + sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001001,
            'func': None,
            'unique': None}

        self.instructions['andi'] = {
            'encoding': '001100{rs}{rt}{immediate}',
            'format': 'andi rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] AND sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001100,
            'func': None,
            'unique': None}

        self.instructions['ori'] = {
            'encoding': '001101{rs}{rt}{immediate}',
            'format': 'ori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] OR sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001101,
            'func': None,
            'unique': None}

        self.instructions['slti'] = {
            'encoding': '001010{rs}{rt}{immediate}',
            'format': 'slti rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001010,
            'func': None,
            'unique': None}

        self.instructions['sltiu'] = {
            'encoding': '001011{rs}{rt}{immediate}',
            'format': 'sltiu rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] < sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001011,
            'func': None,
            'unique': None}

        self.instructions['xori'] = {
            'encoding': '001110{rs}{rt}{immediate}',
            'format': 'xori rt, rs, immediate',
            'desc': 'GPR[rt] = GPR[rs] XOR sign_ext(immediate)',
            'type': InstructionType.I_TYPE,
            'immediate length': 16,
            'op': 0b001110,
            'func': None,
            'unique': None}

        self.instructions['add'] = {
            'encoding': '000000{rs}{rt}{rd}00000100000',
            'format': 'add rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100000,
            'unique': None}

        self.instructions['addu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100001',
            'format': 'addu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] + GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100001,
            'unique': None}

        self.instructions['and'] = {
            'encoding': '000000{rs}{rt}{rd}00000100100',
            'format': 'and rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] AND GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100100,
            'unique': None}

        self.instructions['nor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100111',
            'format': 'nor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] NOR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100111,
            'unique': None}

        self.instructions['or'] = {
            'encoding': '000000{rs}{rt}{rd}00000100101',
            'format': 'or rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] OR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100101,
            'unique': None}

        self.instructions['slt'] = {
            'encoding': '000000{rs}{rt}{rd}00000101010',
            'format': 'slt rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b101010,
            'unique': None}

        self.instructions['sltu'] = {
            'encoding': '000000{rs}{rt}{rd}00000101011',
            'format': 'sltu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] < GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b101011,
            'unique': None}

        self.instructions['sub'] = {
            'encoding': '000000{rs}{rt}{rd}00000100010',
            'format': 'sub rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100010,
            'unique': None}

        self.instructions['subu'] = {
            'encoding': '000000{rs}{rt}{rd}00000100011',
            'format': 'subu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] - GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b100011,
            'unique': None}

        self.instructions['xor'] = {
            'encoding': '000000{rs}{rt}{rd}00000100110',
            'format': 'xor rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] XOR GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b1,
            'unique': None}

        self.instructions['mul'] = {
            'encoding': '000000{rs}{rt}{rd}00010011000',
            'format': 'mul rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011000,
            'unique': (0x000007C0, 0b00010, 6)}

        self.instructions['muh'] = {
            'encoding': '000000{rs}{rt}{rd}00011011000',
            'format': 'muh rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011000,
            'unique': (0x000007C0, 0b00011, 6)}

        self.instructions['mulu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011001',
            'format': 'mulu rd, rs, rt',
            'desc': 'GPR[rd] = lo_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011001,
            'unique': (0x000007C0, 0b00010, 6)}

        self.instructions['muhu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011001',
            'format': 'muhu rd, rs, rt',
            'desc': 'GPR[rd] = hi_word(GPR[rs] x GPR[rt])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011001,
            'unique': (0x000007C0, 0b00011, 6)}

        self.instructions['div'] = {
            'encoding': '000000{rs}{rt}{rd}00010011010',
            'format': 'div rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011010,
            'unique': (0x000007C0, 0b00010, 6)}

        self.instructions['mod'] = {
            'encoding': '000000{rs}{rt}{rd}00011011010',
            'format': 'mod rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011010,
            'unique': (0x000007C0, 0b00011, 6)}

        self.instructions['divu'] = {
            'encoding': '000000{rs}{rt}{rd}00010011011',
            'format': 'divu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] / GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011011,
            'unique': (0x000007C0, 0b00010, 6)}

        self.instructions['modu'] = {
            'encoding': '000000{rs}{rt}{rd}00011011011',
            'format': 'modu rd, rs, rt',
            'desc': 'GPR[rd] = GPR[rs] \\% GPR[rt]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b011011,
            'unique': (0x000007C0, 0b00011, 6)}

        self.instructions['clo'] = {
            'encoding': '000000{rs}00000{rd}00001010001',
            'format': 'clo rd, rs',
            'desc': 'GPR[rd] = count_leading_ones(GPR[rs])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b010001,
            'unique': None}

        self.instructions['clz'] = {
            'encoding': '000000{rs}00000{rd}00001010000',
            'format': 'clz rd, rs',
            'desc': 'GPR[rd] = count_leading_zeroes(GPR[rs])',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b010000,
            'unique': None}

        self.instructions['sll'] = {
            'encoding': '00000000000{rt}{rd}{sa}000000',
            'format': 'sll rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] << sa',
            'type': InstructionType.R_TYPE,
            'immediate length': 5,
            'op': 0b000000,
            'func': 0b000000,
            'unique': None}

        self.instructions['sra'] = {
            'encoding': '00000000000{rt}{rd}{sa}000011',
            'format': 'sra rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] >> sa',
            'type': InstructionType.R_TYPE,
            'immediate length': 5,
            'op': 0b000000,
            'func': 0b000011,
            'unique': None}

        self.instructions['srl'] = {
            'encoding': '00000000000{rt}{rd}{sa}000010',
            'format': 'srl rd, rt, sa',
            'desc': 'GPR[rd] = GPR[rt] >> sa',
            'type': InstructionType.R_TYPE,
            'immediate length': 5,
            'op': 0b000000,
            'func': 0b000010,
            'unique': None}

        self.instructions['sllv'] = {
            'encoding': '000000{rs}{rt}{rd}00000000100',
            'format': 'sllv rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] << GPR[rs]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b000100,
            'unique': None}

        self.instructions['srav'] = {
            'encoding': '000000{rs}{rt}{rd}00000000111',
            'format': 'srav rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] >> GPR[rs]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b000111,
            'unique': None}

        self.instructions['srlv'] = {
            'encoding': '000000{rs}{rt}{rd}00000000110',
            'format': 'srlv rd, rt, rs',
            'desc': 'GPR[rd] = GPR[rt] >> GPR[rs]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b000110,
            'unique': None}

        self.instructions['j'] = {
            'encoding': '000010{target}',
            'format': 'j target',
            'desc': 'set PC = target',
            'type': InstructionType.J_TYPE,
            'immediate length': 26,
            'op': 0b000010,
            'func': None,
            'unique': None}

        self.instructions['jal'] = {
            'encoding': '000011{target}',
            'format': 'jal target',
            'desc': 'set PC = target and link',
            'type': InstructionType.J_TYPE,
            'immediate length': 26,
            'op': 0b000011,
            'func': None,
            'unique': None}

        self.instructions['jalr'] = {
            'encoding': '000000{rs}000001111000000001001',
            'format': 'jalr rs',
            'desc': 'GPR[31] = return_addr, PC = GPR[rs]',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b001001,
            'unique': None}

        self.instructions['jic'] = {
            'encoding': '11011000000{rt}{offset}',
            'format': 'jic rt, offset',
            'desc': 'PC = GPR[rt] + sign_extend(offset)',
            'type': InstructionType.J_TYPE,
            'immediate length': 16,
            'op': 0b110110,
            'func': None,
            'unique': None}

        self.instructions['jialc'] = {
            'encoding': '11111000000{rt}{offset}',
            'format': 'jialc rt, offset',
            'desc': 'GPR[31] = PC+4, PC = GPR[rt] + sign_extend(offset)',
            'type': InstructionType.J_TYPE,
            'immediate length': 16,
            'op': 0b111110,
            'func': None,
            'unique': None}

        self.instructions['bc'] = {
            'encoding': '110010{offset}',
            'format': 'bc offset',
            'desc': 'PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 26,
            'op': 0b110010,
            'func': None,
            'unique': None}

        self.instructions['balc'] = {
            'encoding': '111010{offset}',
            'format': 'balc offset',
            'desc': 'GPR[31] = PC+4, PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 26,
            'op': 0b111010,
            'func': None,
            'unique': None}

        self.instructions['beqzc'] = {
            'encoding': '110110{rs}{offset}',
            'format': 'beqzc rs, offset',
            'desc': 'if GPR[rs] == 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 21,
            'op': 0b110110,
            'func': None,
            'unique': None}

        self.instructions['bnezc'] = {
            'encoding': '111110{rs}{offset}',
            'format': 'bnezc rs, offset',
            'desc': 'if GPR[rs] != 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 21,
            'op': 0b111110,
            'func': None,
            'unique': None}

        self.instructions['blezc'] = {
            'encoding': '01011000000{rt}{offset}',
            'format': 'blezc rt, offset',
            'desc': 'if GPR[rt] < 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b010110,
            'func': None,
            'unique': None}

        self.instructions['bgtzc'] = {
            'encoding': '01011100000{rt}{offset}',
            'format': 'bgtzc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b010111,
            'func': None,
            'unique': None}

        self.instructions['beqzalc'] = {
            'encoding': '00100000000{rt}{offset}',
            'format': 'beqzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b010000,
            'func': None,
            'unique': None}

        self.instructions['bnezalc'] = {
            'encoding': '01100000000{rt}{offset}',
            'format': 'bnezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b011000,
            'func': None,
            'unique': None}

        self.instructions['blezalc'] = {
            'encoding': '00011000000{rt}{offset}',
            'format': 'blezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bgtzalc'] = {
            'encoding': '00011100000{rt}{offset}',
            'format': 'bgtzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['bgezc'] = {
            'encoding': '010110{rt}{rt}{offset}',
            'format': 'bgezc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b010110,
            'func': None,
            'unique': None}

        self.instructions['bltzc'] = {
            'encoding': '010111{rt}{rt}{offset}',
            'format': 'bltzc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b010111,
            'func': None,
            'unique': None}

        self.instructions['bgezalc'] = {
            'encoding': '000110{rt}{rt}{offset}',
            'format': 'bgezalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bltzalc'] = {
            'encoding': '000111{rt}{rt}{offset}',
            'format': 'bltzalc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['beq'] = {
            'encoding': '000100{rs}{rt}{offset}',
            'format': 'beq rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000100,
            'func': None,
            'unique': None}

        self.instructions['bne'] = {
            'encoding': '000101{rs}{rt}{offset}',
            'format': 'bne rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000101,
            'func': None,
            'unique': None}

        self.instructions['bgeuc'] = {
            'encoding': '000110{rs}{rt}{offset}',
            'format': 'bgeuc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000110,
            'func': None,
            'unique': None}

        self.instructions['bltuc'] = {
            'encoding': '000111{rs}{rt}{offset}',
            'format': 'bltuc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000111,
            'func': None,
            'unique': None}

        self.instructions['bovc'] = {
            'encoding': '001000{rs}{rt}{offset}',
            'format': 'bovc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b001000,
            'func': None,
            'unique': None}

        self.instructions['bnvc'] = {
            'encoding': '011000{rs}{rt}{offset}',
            'format': 'bnvc rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b011000,
            'func': None,
            'unique': None}

        self.instructions['bgez'] = {
            'encoding': '000001{rs}00001{offset}',
            'format': 'bgez rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000001,
            'func': None,
            'unique': (0x001F0000, 0b00001, 16)}

        self.instructions['bgtz'] = {
            'encoding': '000111{rs}00000{offset}',
            'format': 'bgtz rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000111,
            'func': None,
            'unique': (0x001F0000, 0b00000, 16)}

        self.instructions['blez'] = {
            'encoding': '000110{rs}00000{offset}',
            'format': 'blez rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000110,
            'func': None,
            'unique': (0x001F0000, 0b00000, 16)}

        self.instructions['bltz'] = {
            'encoding': '000001{rs}00000{offset}',
            'format': 'bltz rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.I_B_TYPE,
            'immediate length': 16,
            'op': 0b000001,
            'func': None,
            'unique': (0x001F0000, 0b00000, 16)}

        self.instructions['mfc0'] = {
            'encoding': '01000000000{rt}{rd}00000000000',
            'format': 'mfc0 rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b010000,
            'func': 0b000000,
            'unique': (0x03E00000, 0b00000, 21)}

        self.instructions['mtc0'] = {
            'encoding': '01000000100{rt}{rd}00000000000',
            'format': 'mtc0 rt, offset',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b010000,
            'func': 0b000000,
            'unique': (0x03E00000, 0b00100, 21)}

        self.instructions['syscall'] = {
            'encoding': '00000000000000000000000000001100',
            'format': 'syscall',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b001100,
            'unique': None}

        self.instructions['break'] = {
            'encoding': '00000000000000000000000000001101',
            'format': 'break',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b001101,
            'unique': None}

        self.instructions['nop'] = {
            'encoding': '00000000000000000000000000000000',
            'format': 'break',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b000000,
            'unique': (0xFFFFFFFF, 0x00000000, 0)}

        self.instructions['teq'] = {
            'encoding': '000000{rs}{rt}0000000000110100',
            'format': 'teq rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110100,
            'unique': None}

        self.instructions['tge'] = {
            'encoding': '000000{rs}{rt}0000000000110000',
            'format': 'tge rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110000,
            'unique': None}

        self.instructions['tgeu'] = {
            'encoding': '000000{rs}{rt}0000000000110001',
            'format': 'tgeu rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110001,
            'unique': None}

        self.instructions['tlt'] = {
            'encoding': '000000{rs}{rt}0000000000110010',
            'format': 'tlt rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110010,
            'unique': None}

        self.instructions['tltu'] = {
            'encoding': '000000{rs}{rt}0000000000110011',
            'format': 'tltu rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110011,
            'unique': None}

        self.instructions['tne'] = {
            'encoding': '000000{rs}{rt}0000000000110110',
            'format': 'tne rs, rt',
            'desc': 'if GPR[rt] > 0: PC = PC+4 + sign_extend(offset << 2)',
            'type': InstructionType.R_TYPE,
            'immediate length': None,
            'op': 0b000000,
            'func': 0b110110,
            'unique': None}

    def get_op(self, instr: int) -> int:
        """
        Returns the op code of the binary instruction
        """
        return (instr & self.OP_MASK) >> 26
    
    def get_func(self, instr: int) -> int:
        """
        Returns func code of the binary instruction
        """
        return instr & self.FUNC_MASK
    
    def get_reg1(self, instr: int) -> int:
        """
        Return bits 25-21 from instr
        """
        return (instr & self.REG1_MASK[0]) >> self.REG1_MASK[1]
    
    def get_reg2(self, instr: int) -> int:
        """
        Return bits 20-16 from instr
        """
        return (instr & self.REG2_MASK[0]) >> self.REG2_MASK[1]
    
    def get_reg3(self, instr: int) -> int:
        """
        Return bits 15-11 from instr
        """
        return (instr & self.REG3_MASK[0]) >> self.REG3_MASK[1]
    
    def get_i16(self, instr: int) -> int:
        """
        Return 16-bit immediate from instr
        """
        return instr & self.I16_MASK

    # The following functions are used to execute the different mips instructions

    def load_store(self, instr: int):
        """
        Simulates load/store instructions
        """
        instr_op = self.get_op(instr)
        base = self.get_reg1(instr)
        rt = self.get_reg2(instr)
        offset = self.get_i16(instr)
        
        if instr_op == self.instructions['lb']['op']:
            # LB
            pass
