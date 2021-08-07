"""
MIPS32 simulation functions are placed here

The names of the functions should match the 
instruction mnemonic followed by _instruction
For example: def add_instruction()
"""

import inspect
import sys
from typing import Callable, overload
from ctypes import c_uint16, c_uint32, c_int32
import json

from ..hardware import memory, registers, alu
from ..hardware.memory import MemorySize
from .exceptions import *
from ..utils import Integer

GPRLEN = 32
GPR_RA = 31

def get_sim_function_by_mnemonic(mnemonic: str) -> Callable[[int], None]:
    """
    Get an instruction's simulation function by mnemonic
    """

    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if mnemonic == name.replace('_instruction', '') and inspect.isfunction(obj):
            return obj


def add_instruction(instr):
    """
    MIPS32 ADD simulation function
    """

    rd = instr.tokens[1].value
    rs = instr.tokens[2].value
    rt = instr.tokens[3].value
    res, overflow = alu.add32(registers.gpr_read(rs), registers.gpr_read(rt))
    if overflow:
        raise IntegerOverflow
    registers.gpr_write(rd, res)


def addiu_instruction(instr):
    """
    MIPS32 ADDIU simulation function
    """

    rt = instr.tokens[1].value
    rs = instr.tokens[2].value
    imm = instr.tokens[3].value
    res, overflow = alu.add32(registers.gpr_read(rs), imm)
    registers.gpr_write(rt, res)


def addiupc_instruction(instr):
    """
    MIPS32 ADDIUPC simulation function
    """

    rs = instr.tokens[1].value
    imm = instr.tokens[2].value
    res, overflow = alu.add32(registers.pc, imm << 2)
    registers.gpr_write(rs, res)


def addu_instruction(instr):
    """
    MIPS32 ADDU simulation function
    """

    rd = instr.tokens[1].value
    rs = instr.tokens[2].value
    rt = instr.tokens[3].value
    res, overflow = alu.add32(registers.gpr_read(rs), registers.gpr_read(rt))
    registers.gpr_write(rd, res)


def align_instruction(instr):
    """
    MIPS32 ALIGN simulation function
    """

    rd = instr.tokens[1].value
    rs = instr.tokens[2].value
    rt = instr.tokens[3].value
    bp = instr.tokens[4].value
    res = (registers.gpr_read(rt) << (8*bp)
           ) | (registers.gpr_read(rs) >> (GPRLEN-8*bp))
    registers.gpr_write(rd, res)


def aluipc_instruction(instr):
    """
    MIPS32 ALUIPC simulation function
    """

    rs = instr.tokens[1].value
    imm = instr.tokens[2].value
    res, overflow = alu.add32(registers.pc, imm << 16)
    res = alu.and32(~0x0FFFF, res)
    registers.gpr_write(rs, res)


def and_instruction(instr):
    """
    MIPS32 AND simulation function
    """

    rd = instr.tokens[1].value
    rs = instr.tokens[2].value
    rt = instr.tokens[3].value
    res = alu.and32(registers.gpr_read(rs), registers.gpr_read(rt))
    registers.gpr_write(rd, res)


def andi_instruction(instr):
    """
    MIPS32 ANDI simulation function
    """

    rt = instr.tokens[1].value
    rs = instr.tokens[2].value
    imm = instr.tokens[3].value
    res = alu.and32(registers.gpr_read(rs), imm)
    registers.gpr_write(rt, res)


def aui_instruction(instr):
    """
    MIPS32 AUI simulation function
    """

    rt = instr.tokens[1].value
    rs = instr.tokens[2].value
    imm = instr.tokens[3].value
    res, overflow = alu.add32(registers.gpr_read(rs), imm << 16)
    registers.gpr_write(rt, res)


def auipc_instruction(instr):
    """
    MIPS32 AUIPC simulation function
    """

    rs = instr.tokens[1].value
    imm = instr.tokens[2].value
    res, overflow = alu.add32(registers.pc, imm << 16)
    registers.gpr_write(rs, res)


def bal_instruction(instr):
    """
    MIPS32 BAL simulation function
    """

    offset = instr.tokens[1].value
    registers.gpr_write(GPR_RA, registers.pc+4)
    registers.pc = alu.add32(registers.pc, offset << 2)


def balc_instruction(instr):
	"""
	MIPS32 BALC SIMULATION FUNCTION
	"""

	offset = instr.tokens[1].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	registers.pc = alu.add32(registers.pc, offset << 2)

def bc_instruction(instr):
	"""
	MIPS32 BC SIMULATION FUNCTION
	"""

	offset = instr.tokens[1].value
	registers.pc = alu.add32(registers.pc, offset << 2)

def beq_instruction(instr):
	"""
	MIPS32 BEQ SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if registers.gpr_read(rs) == registers.gpr_read(rt):
		registers.pc = alu.add32(registers.pc, offset << 2)

def beqzalc_instruction(instr):
	"""
	MIPS32 BEQZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt) == 0:
		registers.pc = alu.add32(registers.pc, offset << 2)
	
def beqzc_instruction(instr):
	"""
	MIPS32 BEQZC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rs) == 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgec_instruction(instr):
	"""
	MIPS32 BGEC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if (registers.gpr_read(rs, signed=True) >= registers.gpr_read(rt, signed=True)):
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgeuc_instruction(instr):
	"""
	MIPS32 BGEUC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if registers.gpr_read(rs) >= registers.gpr_read(rt):
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgez_instruction(instr):
	"""
	MIPS32 BGEZ SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rs, signed=True) >= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgezalc_instruction(instr):
	"""
	MIPS32 BGEZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt, signed=True) >= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgezc_instruction(instr):
	"""
	MIPS32 BGEZC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rt, signed=True) >= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgtz_instruction(instr):
	"""
	MIPS32 BGEZ SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rs, signed=True) > 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgtzalc_instruction(instr):
	"""
	MIPS32 BGEZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt, signed=True) > 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bgtzc_instruction(instr):
	"""
	MIPS32 BGEZC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rt, signed=True) > 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bitswap_instruction(instr):
	"""
	MIPS32 BITSWAP SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	tmp_bytes = []
	rt_val = registers.gpr_read(rt)
	for i in range(MemorySize.WORD_LENGTH_BYTES):
		tmp_byte = Integer.get_byte(rt_val, i)
		tmp_bytes.append('{:08b}'.format(tmp_byte)[::-1])
	registers.gpr_write(rd, int(''.join(tmp_bytes[::-1]), 2))

def blez_instruction(instr):
	"""
	MIPS32 BLEZ SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rs, signed=True) <= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def blezalc_instruction(instr):
	"""
	MIPS32 BLEZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt, signed=True) <= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def blezc_instruction(instr):
	"""
	MIPS32 BLEZC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rt, signed=True) <= 0:
		registers.pc = alu.add32(registers.pc, offset << 2)
	
def bltc_instruction(instr):
	"""
	MIPS32 BLTC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if registers.gpr_read(rs, signed=True) <= registers.gpr_read(rt, signed=True):
		registers.pc = alu.add32(registers.pc, offset << 2)

def bltuc_instruction(instr):
	"""
	MIPS32 BLTUC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if registers.gpr_read(rs) <= registers.gpr_read(rt):
		registers.pc = alu.add32(registers.pc, offset << 2)

def bltz_instruction(instr):
	"""
	MIPS32 BLTZ SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rt, signed=True) < 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bltzalc_instruction(instr):
	"""
	MIPS32 BLTZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt, signed=True) < 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bltzc_instruction(instr):
	"""
	MIPS32 BLTZ SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rt, signed=True) < 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bne_instruction(instr):
	"""
	MIPS32 BNE SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	if registers.gpr_read(rs) != registers.gpr_read(rt):
		registers.pc = alu.add32(registers.pc, offset << 2)

def bnezalc_instruction(instr):
	"""
	MIPS32 BNEZALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	if registers.gpr_read(rt) != 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bnezc_instruction(instr):
	"""
	MIPS32 BNEZC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	if registers.gpr_read(rs) != 0:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bnvc_instruction(instr):
	"""
	MIPS32 BNVC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	res, overflow = alu.add32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	if not overflow:
		registers.pc = alu.add32(registers.pc, offset << 2)

def bovc_instruction(instr):
	"""
	MIPS32 BOVC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	offset = instr.tokens[3].value
	res, overflow = alu.add32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	if overflow:
		registers.pc = alu.add32(registers.pc, offset << 2)

def break_instruction(instr):
	"""
	MIPS32 BREAK SIMULATION FUNCTION
	"""

	raise BreakpointException

def clo_instruction(instr):
	"""
	MIPS32 CLO SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	i = GPR_RA
	rs_val = registers.gpr_read(rs)
	cnt = 0
	while (Integer.get_bit(rs_val, i) == 1) and i >= 0:
		cnt += 1
		i -= 1
	registers.gpr_write(rd, cnt)

def clz_instruction(instr):
	"""
	MIPS32 CLZ SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	i = GPR_RA
	rs_val = registers.gpr_read(rs)
	cnt = 0
	while (Integer.get_bit(rs_val, i) == 0) and i >= 0:
		cnt += 1
		i -= 1
	registers.gpr_write(rd, cnt)

def div_instruction(instr):
	"""
	MIPS32 DIV SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.div32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	registers.gpr_write(rd, res)

def divu_instruction(instr):
	"""
	MIPS32 DIVU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.div32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def j_instruction(instr):
	"""
	MIPS32 J SIMULATION FUNCTION
	"""

	target = instr.tokens[1].value
	# After instruction is simulated, 4 is added to pc
	registers.pc = (target << 2) - 4

def jal_instruction(instr):
	"""
	MIPS32 JAL SIMULATION FUNCTION
	"""

	target = instr.tokens[1].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	# After instruction is simulated, 4 is added to pc
	registers.pc = (target << 2) - 4

def jalr_instruction(instr):
	"""
	MIPS32 JALR SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	registers.gpr_write(rd, registers.pc+4)
	# After instruction is simulated, 4 is added to pc
	new_pc = registers.gpr_read(rs)
	if not memory.is_aligned(new_pc, MemorySize.WORD):
		raise AddressError
	registers.pc = new_pc

def jialc_instruction(instr):
	"""
	MIPS32 JIALC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	registers.gpr_write(GPR_RA, registers.pc+4)
	# After instruction is simulated, 4 is added to pc
	new_pc = alu.add32(registers.gpr_read(rt, signed=True), offset)
	if not memory.is_aligned(new_pc, MemorySize.WORD):
		raise AddressError
	registers.pc = new_pc

def jic_instruction(instr):
	"""
	MIPS32 JIC SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	# After instruction is simulated, 4 is added to pc
	new_pc = alu.add32(registers.gpr_read(rt, signed=True), offset)
	if not memory.is_aligned(new_pc, MemorySize.WORD):
		raise AddressError
	registers.pc = new_pc

def lb_instruction(instr):
	"""
	MIPS32 LB SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		res = memory.read_byte(addr=addr, signed=True)
		registers.gpr_write(rt, res)
	except MemoryError:
		raise AddressError

def lbu_instruction(instr):
	"""
	MIPS32 LBU SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		res = memory.read_byte(addr=addr)
		registers.gpr_write(rt, res)
	except MemoryError:
		raise AddressError

def lh_instruction(instr):
	"""
	MIPS32 LH SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		res = memory.read_hword(addr=addr, signed=True)
		registers.gpr_write(rt, res)
	except MemoryError:
		raise AddressError

def lhu_instruction(instr):
	"""
	MIPS32 LHU SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		res = memory.read_hword(addr=addr)
		registers.gpr_write(rt, res)
	except MemoryError:
		raise AddressError

def lw_instruction(instr):
	"""
	MIPS32 LW SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr, overflow = alu.add32(registers.gpr_read(base), offset)
	try:
		res = memory.read_word(addr=addr, signed=True)
		registers.gpr_write(rt, res)
	except MemoryError:
		raise AddressError

def lwpc_instruction(instr):
	"""
	MIPS32 LWPC SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	offset = instr.tokens[2].value
	addr, overflow = alu.add32(registers.pc, offset << 2)
	try:
		res = memory.read_word(addr=addr, signed=True)
		registers.gpr_write(rs, res)
	except MemoryError:
		raise AddressError

def mfc0_instruction(instr):
	"""
	MIPS32 MFC0 SIMULATION FUNCTION
	"""

	pass

def mod_instruction(instr):
	"""
	MIPS32 MOD SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.mod32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	registers.gpr_write(rd, res)

def modu_instruction(instr):
	"""
	MIPS32 MODU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.mod32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def mtc0_instruction(instr):
	"""
	MIPS32 MTC0 SIMULATION FUNCTION
	"""

	pass

def muh_instruction(instr):
	"""
	MIPS32 MUH SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.muh32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	registers.gpr_write(rd, res)

def muhu_instruction(instr):
	"""
	MIPS32 MUHU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.muh32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def mul_instruction(instr):
	"""
	MIPS32 MUL SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.mul32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	registers.gpr_write(rd, res)

def mulu_instruction(instr):
	"""
	MIPS32 MULU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.mul32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def nor_instruction(instr):
	"""
	MIPS32 NOR SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.nor32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def or_instruction(instr):
	"""
	MIPS32 NOR SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.or32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def or_instruction(instr):
	"""
	MIPS32 NOR SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	rs = instr.tokens[2].value
	imm = instr.tokens[3].value
	res = alu.or32(registers.gpr_read(rs), imm)
	registers.gpr_write(rt, res)

def sb_instruction(instr):
	"""
	MIPS32 SB SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		memory.write(addr, registers.gpr_read(rt), MemorySize.BYTE)
	except MemoryError:
		raise AddressError

def sh_instruction(instr):
	"""
	MIPS32 SH SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		memory.write(addr, registers.gpr_read(rt), MemorySize.HWORD)
	except MemoryError:
		raise AddressError

def sll_instruction(instr):
	"""
	MIPS32 SLL SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	sa = instr.tokens[3].value
	res = alu.shift_left32(registers.gpr_read(rt), sa)
	registers.gpr_write(rd, res)

def sllv_instruction(instr):
	"""
	MIPS32 SLLV SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	rs = instr.tokens[3].value
	res = alu.shift_left32(registers.gpr_read(rt), registers.gpr_read(rs))
	registers.gpr_write(rd, res)

def slt_instruction(instr):
	"""
	MIPS32 SLT SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = registers.gpr_read(rs, signed=True) < registers.gpr_read(rt, signed=True)
	registers.gpr_write(rd, int(res))

def slti_instruction(instr):
	"""
	MIPS32 SLTI SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	rs = instr.tokens[2].value
	imm = instr.tokens[3].value
	res = registers.gpr_read(rs, signed=True) < imm
	registers.gpr_write(rt, int(res))

def sltiu_instruction(instr):
	"""
	MIPS32 SLTUI SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	rs = instr.tokens[2].value
	imm = instr.tokens[3].value
	res = registers.gpr_read(rs) < c_uint16(imm)
	registers.gpr_write(rt, int(res))

def sltu_instruction(instr):
	"""
	MIPS32 SLTU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = registers.gpr_read(rs) < registers.gpr_read(rt)
	registers.gpr_write(rd, int(res))

def sra_instruction(instr):
	"""
	MIPS32 SRA SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	sa = instr.tokens[3].value
	res = alu.shift_right32(registers.gpr_read(rt), sa, sign=True)
	registers.gpr_write(rd, res)

def srav_instruction(instr):
	"""
	MIPS32 SRA SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	rs = instr.tokens[3].value
	res = alu.shift_right32(registers.gpr_read(rt), registers.gpr_read(rs), sign=True)
	registers.gpr_write(rd, res)

def srl_instruction(instr):
	"""
	MIPS32 SRL SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	sa = instr.tokens[3].value
	res = alu.shift_right32(registers.gpr_read(rt), sa)
	registers.gpr_write(rd, res)

def srlv_instruction(instr):
	"""
	MIPS32 SRL SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rt = instr.tokens[2].value
	rs = instr.tokens[3].value
	res = alu.shift_right32(registers.gpr_read(rt), registers.gpr_read(rs))
	registers.gpr_write(rd, res)

def sub_instruction(instr):
	"""
	MIPS32 SUB SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.sub32(registers.gpr_read(rs, signed=True), registers.gpr_read(rt, signed=True))
	registers.gpr_write(rd, res)

def subu_instruction(instr):
	"""
	MIPS32 SUBU SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.sub32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def sw_instruction(instr):
	"""
	MIPS32 SW SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	offset = instr.tokens[2].value
	base = instr.tokens[4].value # tokens[3] is left parenthesis
	addr = alu.add32(registers.gpr_read(base), offset)
	try:
		memory.write(addr, registers.gpr_read(rt), MemorySize.WORD)
	except MemoryError:
		raise AddressError

def syscall_instruction(instr):
	"""
	MIPS32 SYSCALL SIMULATION FUNCTION
	"""

	raise SystemCall

def teq_instruction(instr):
	"""
	MIPS32 TEQ SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs) == registers.gpr_read(rt):
		raise Trap

def tge_instruction(instr):
	"""
	MIPS32 TGE SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs, signed=True) >= registers.gpr_read(rt, signed=True):
		raise Trap
	
def tgeu_instruction(instr):
	"""
	MIPS32 TGEU SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs) >= registers.gpr_read(rt):
		raise Trap

def tlt_instruction(instr):
	"""
	MIPS32 TLT SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs, signed=True) < registers.gpr_read(rt, signed=True):
		raise Trap

def tltu_instruction(instr):
	"""
	MIPS32 TLTU SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs) < registers.gpr_read(rt):
		raise Trap

def tne_instruction(instr):
	"""
	MIPS32 TNE SIMULATION FUNCTION
	"""

	rs = instr.tokens[1].value
	rt = instr.tokens[2].value
	if registers.gpr_read(rs) != registers.gpr_read(rt):
		raise Trap

def xor_instruction(instr):
	"""
	MIPS32 XOR SIMULATION FUNCTION
	"""

	rd = instr.tokens[1].value
	rs = instr.tokens[2].value
	rt = instr.tokens[3].value
	res = alu.xor32(registers.gpr_read(rs), registers.gpr_read(rt))
	registers.gpr_write(rd, res)

def xori_instruction(instr):
	"""
	MIPS32 XOR SIMULATION FUNCTION
	"""

	rt = instr.tokens[1].value
	rs = instr.tokens[2].value
	imm = instr.tokens[3].value
	res = alu.xor32(registers.gpr_read(rs), imm)
	registers.gpr_write(rt, res)