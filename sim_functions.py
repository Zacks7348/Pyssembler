"""
MIPS32 simulation functions are placed here

The names of the functions should match the 
instruction mnemonic followed by _instruction
For example: def add_instruction()
"""

import inspect
import sys
from typing import Callable, overload
from ctypes import c_uint32, c_int32
import json

from ..hardware import memory, registers, alu
from .exceptions import *
from ..utils import Integer

GPRLEN = 32

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
	if overflow: raise IntegerOverflow
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
	res = (registers.gpr_read(rt) << (8*bp)) | (registers.gpr_read(rs) >> (GPRLEN-8*bp))
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
	registers.gpr_write(31, registers.pc+4)
	registers.pc = alu.add32(registers.pc, offset << 2)

def balc_instruction(instr):
    """
    MIPS32 BALC SIMULATION FUNCTION
    """

    pass
def bc_instruction(instr):
    """
    MIPS32 BC SIMULATION FUNCTION
    """

    pass
def beq_instruction(instr):
    """
    MIPS32 BEQ SIMULATION FUNCTION
    """

    pass
def beqzalc_instruction(instr):
    """
    MIPS32 BEQZALC SIMULATION FUNCTION
    """

    pass
def beqzc_instruction(instr):
    """
    MIPS32 BEQZC SIMULATION FUNCTION
    """

    pass
def bgec_instruction(instr):
    """
    MIPS32 BGEC SIMULATION FUNCTION
    """

    pass
def bgeuc_instruction(instr):
    """
    MIPS32 BGEUC SIMULATION FUNCTION
    """

    pass
def bgez_instruction(instr):
    """
    MIPS32 BGEZ SIMULATION FUNCTION
    """

    pass
def bgezalc_instruction(instr):
    """
    MIPS32 BGEZALC SIMULATION FUNCTION
    """

    pass
def bgezc_instruction(instr):
    """
    MIPS32 BGEZC SIMULATION FUNCTION
    """

    pass
def bgtz_instruction(instr):
    """
    MIPS32 BGTZ SIMULATION FUNCTION
    """

    pass
def bgtzalc_instruction(instr):
    """
    MIPS32 BGTZALC SIMULATION FUNCTION
    """

    pass
def bgtzc_instruction(instr):
    """
    MIPS32 BGTZC SIMULATION FUNCTION
    """

    pass
def bitswap_instruction(instr):
    """
    MIPS32 BITSWAP SIMULATION FUNCTION
    """

    pass
def blez_instruction(instr):
    """
    MIPS32 BLEZ SIMULATION FUNCTION
    """

    pass
def blezalc_instruction(instr):
    """
    MIPS32 BLEZALC SIMULATION FUNCTION
    """

    pass
def blezc_instruction(instr):
    """
    MIPS32 BLEZC SIMULATION FUNCTION
    """

    pass
def bltc_instruction(instr):
    """
    MIPS32 BLTC SIMULATION FUNCTION
    """

    pass
def bltuc_instruction(instr):
    """
    MIPS32 BLTUC SIMULATION FUNCTION
    """

    pass
def bltz_instruction(instr):
    """
    MIPS32 BLTZ SIMULATION FUNCTION
    """

    pass
def bltzalc_instruction(instr):
    """
    MIPS32 BLTZALC SIMULATION FUNCTION
    """

    pass
def bltzc_instruction(instr):
    """
    MIPS32 BLTZC SIMULATION FUNCTION
    """

    pass
def bne_instruction(instr):
    """
    MIPS32 BNE SIMULATION FUNCTION
    """

    pass
def bnezalc_instruction(instr):
    """
    MIPS32 BNEZALC SIMULATION FUNCTION
    """

    pass
def bnezc_instruction(instr):
    """
    MIPS32 BNEZC SIMULATION FUNCTION
    """

    pass
def bnvc_instruction(instr):
    """
    MIPS32 BNVC SIMULATION FUNCTION
    """

    pass
def bovc_instruction(instr):
    """
    MIPS32 BOVC SIMULATION FUNCTION
    """

    pass
def break_instruction(instr):
    """
    MIPS32 BREAK SIMULATION FUNCTION
    """

    pass
def clo_instruction(instr):
    """
    MIPS32 CLO SIMULATION FUNCTION
    """

    pass
def clz_instruction(instr):
    """
    MIPS32 CLZ SIMULATION FUNCTION
    """

    pass
def div_instruction(instr):
    """
    MIPS32 DIV SIMULATION FUNCTION
    """

    pass
def divu_instruction(instr):
    """
    MIPS32 DIVU SIMULATION FUNCTION
    """

    pass
def j_instruction(instr):
    """
    MIPS32 J SIMULATION FUNCTION
    """

    pass
def jal_instruction(instr):
    """
    MIPS32 JAL SIMULATION FUNCTION
    """

    pass
def jalr_instruction(instr):
    """
    MIPS32 JALR SIMULATION FUNCTION
    """

    pass
def jialc_instruction(instr):
    """
    MIPS32 JIALC SIMULATION FUNCTION
    """

    pass
def jic_instruction(instr):
    """
    MIPS32 JIC SIMULATION FUNCTION
    """

    pass
def lb_instruction(instr):
    """
    MIPS32 LB SIMULATION FUNCTION
    """

    pass
def lbu_instruction(instr):
    """
    MIPS32 LBU SIMULATION FUNCTION
    """

    pass
def lh_instruction(instr):
    """
    MIPS32 LH SIMULATION FUNCTION
    """

    pass
def lhu_instruction(instr):
    """
    MIPS32 LHU SIMULATION FUNCTION
    """

    pass
def lw_instruction(instr):
    """
    MIPS32 LW SIMULATION FUNCTION
    """

    pass
def lwpc_instruction(instr):
    """
    MIPS32 LWPC SIMULATION FUNCTION
    """

    pass
def mfc0_instruction(instr):
    """
    MIPS32 MFC0 SIMULATION FUNCTION
    """

    pass
def mod_instruction(instr):
    """
    MIPS32 MOD SIMULATION FUNCTION
    """

    pass
def modu_instruction(instr):
    """
    MIPS32 MODU SIMULATION FUNCTION
    """

    pass
def mtc0_instruction(instr):
    """
    MIPS32 MTC0 SIMULATION FUNCTION
    """

    pass
def muh_instruction(instr):
    """
    MIPS32 MUH SIMULATION FUNCTION
    """

    pass
def muhu_instruction(instr):
    """
    MIPS32 MUHU SIMULATION FUNCTION
    """

    pass
def mul_instruction(instr):
    """
    MIPS32 MUL SIMULATION FUNCTION
    """

    pass
def mulu_instruction(instr):
    """
    MIPS32 MULU SIMULATION FUNCTION
    """

    pass
def nor_instruction(instr):
    """
    MIPS32 NOR SIMULATION FUNCTION
    """

    pass
def or_instruction(instr):
    """
    MIPS32 OR SIMULATION FUNCTION
    """

    pass
def ori_instruction(instr):
    """
    MIPS32 ORI SIMULATION FUNCTION
    """

    pass
def sb_instruction(instr):
    """
    MIPS32 SB SIMULATION FUNCTION
    """

    pass
def sh_instruction(instr):
    """
    MIPS32 SH SIMULATION FUNCTION
    """

    pass
def sll_instruction(instr):
    """
    MIPS32 SLL SIMULATION FUNCTION
    """

    pass
def sllv_instruction(instr):
    """
    MIPS32 SLLV SIMULATION FUNCTION
    """

    pass
def slt_instruction(instr):
    """
    MIPS32 SLT SIMULATION FUNCTION
    """

    pass
def slti_instruction(instr):
    """
    MIPS32 SLTI SIMULATION FUNCTION
    """

    pass
def slti_instruction(instr):
    """
    MIPS32 SLTI SIMULATION FUNCTION
    """

    pass
def sltu_instruction(instr):
    """
    MIPS32 SLTU SIMULATION FUNCTION
    """

    pass
def sra_instruction(instr):
    """
    MIPS32 SRA SIMULATION FUNCTION
    """

    pass
def srav_instruction(instr):
    """
    MIPS32 SRAV SIMULATION FUNCTION
    """

    pass
def srl_instruction(instr):
    """
    MIPS32 SRL SIMULATION FUNCTION
    """

    pass
def srlv_instruction(instr):
    """
    MIPS32 SRLV SIMULATION FUNCTION
    """

    pass
def sub_instruction(instr):
    """
    MIPS32 SUB SIMULATION FUNCTION
    """

    pass
def subu_instruction(instr):
    """
    MIPS32 SUBU SIMULATION FUNCTION
    """

    pass
def sw_instruction(instr):
    """
    MIPS32 SW SIMULATION FUNCTION
    """

    pass
def syscall_instruction(instr):
    """
    MIPS32 SYSCALL SIMULATION FUNCTION
    """

    pass
def teq_instruction(instr):
    """
    MIPS32 TEQ SIMULATION FUNCTION
    """

    pass
def tge_instruction(instr):
    """
    MIPS32 TGE SIMULATION FUNCTION
    """

    pass
def tgeu_instruction(instr):
    """
    MIPS32 TGEU SIMULATION FUNCTION
    """

    pass
def tlt_instruction(instr):
    """
    MIPS32 TLT SIMULATION FUNCTION
    """

    pass
def tltu_instruction(instr):
    """
    MIPS32 TLTU SIMULATION FUNCTION
    """

    pass
def tne_instruction(instr):
    """
    MIPS32 TNE SIMULATION FUNCTION
    """

    pass
def xor_instruction(instr):
    """
    MIPS32 XOR SIMULATION FUNCTION
    """

    pass
def xori_instruction(instr):
    """
    MIPS32 XORI SIMULATION FUNCTION
    """

    pass
