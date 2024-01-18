import typing

from ..common.cpu import MIPSCPU
from .hardware.memory import MIPS32Memory
from .hardware.register import *
from .instructions import MIPS32InstructionSet, yield_basic_instr_cls
from pyssembler.architecture import core
from pyssembler.architecture.mips.common.mips_program import MIPSProgram


class MIPS32CPU(MIPSCPU):
    def clear_program_memory(self) -> None:
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._instr_set: MIPS32InstructionSet = MIPS32InstructionSet()
        self._memory: MIPS32Memory = MIPS32Memory()
        self._pc: MIPS32Register = MIPS32Register(0, 'PC')
        self._gpr: GeneralPurposeRegisters = GeneralPurposeRegisters()
        self._fpr: FloatingPointRegisters = FloatingPointRegisters()

        for instr_cls in yield_basic_instr_cls():
            instr = instr_cls(self)
            self._instr_set.add_instruction(instr)

    @property
    def instruction_set(self) -> MIPS32InstructionSet:
        return self._instr_set

    @property
    def memory(self) -> MIPS32Memory:
        return self._memory

    @property
    def pc(self) -> MIPSRegister:
        return self._pc

    @property
    def gpr(self) -> GeneralPurposeRegisters:
        return self._gpr

    @property
    def fpr(self) -> FloatingPointRegisters:
        return self._fpr

    def get_register_names(self) -> typing.List[str]:
        return self._gpr.register_names + self._fpr.register_names

    def get_register_address(self, name: str) -> int:
        if name in self._gpr.register_names:
            return self._gpr.get_register(name=name).address

        if name in self._fpr.register_names:
            return self._fpr.get_register(name=name).address

    def load_program_to_memory(self, program: MIPSProgram) -> None:
        self.assembler.assemble_program(
            program,
            user_text_ptr=self.memory.config.text_lower_addr,
            user_data_ptr=self.memory.config.data_lower_addr,
            kernel_text_ptr=self.memory.config.ktext_lower_addr,
            kernel_data_ptr=self.memory.config.kdata_lower_addr,
        )
        self.pc.write_integer(self.memory.config.text_lower_addr)
