from __future__ import annotations
import inspect
import logging
from typing import Dict, List, Type, TYPE_CHECKING

from pyssembler.mips.instructions import basic_instructions
from pyssembler.mips.instructions.base_instruction import MIPSBasicInstruction, MIPSPseudoInstruction

if TYPE_CHECKING:
    from pyssembler.mips.instructions.base_instruction import MIPSInstruction
    from pyssembler.mips.statement import MIPSStatement


__LOGGER__ = logging.getLogger(__name__)

__LOGGER__.debug('Building MIPS Instruction Set...')
BASIC_INSTRUCTIONS: Dict[str, MIPSBasicInstruction] = {}
for _name, _obj in inspect.getmembers(basic_instructions):
    if inspect.isclass(_obj):
        if issubclass(_obj, MIPSBasicInstruction) and _obj is not MIPSBasicInstruction:
            _mnemonic = _obj.mnemonic()
            BASIC_INSTRUCTIONS[_mnemonic] = _obj()

PSUEDO_INSTRUCTIONS: Dict[str, List[Type[MIPSPseudoInstruction]]] = {}
# TODO: Build dictionary of psuedo instructions


def match_instruction(statement: MIPSStatement) -> MIPSInstruction:
    # __LOGGER__.debug(f'Matching {statement} to an instruction...')
    # Check if basic instruction
    instruction = BASIC_INSTRUCTIONS.get(statement.tokens[0].value, None)
    if not instruction:
        __LOGGER__.debug(f'{statement.tokens[0]} is not a valid mnemonic!')
        return None
    # Check if statement actually matches
    if not instruction.match(statement):
        __LOGGER__.debug(f'{statement} does not match basic instruction {instruction}!')
        return None
    return instruction


def get_mnemonic_descriptions(mnemonic: str) -> str:
    descriptions = ''
    if mnemonic in BASIC_INSTRUCTIONS:
        instr = BASIC_INSTRUCTIONS[mnemonic]
        descriptions += f'{instr.format}: {instr.description}\n'

    return descriptions

