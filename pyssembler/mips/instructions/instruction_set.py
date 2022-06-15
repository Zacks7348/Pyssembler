from __future__ import annotations
import inspect
from typing import Dict, List, TYPE_CHECKING

from pyssembler.mips.instructions import basic_instructions

if TYPE_CHECKING:
    from pyssembler.mips.tokenizer import Token

BASIC_INSTRUCTIONS: Dict[str, basic_instructions.MIPSBaseInstruction] = {}
for name, obj in inspect.getmembers(basic_instructions):
    if inspect.isclass(obj):
        if name.startswith('MIPS') and name.endswith('Instruction'):
            if (mnemonic := obj.MNEMONIC) is not None:
                BASIC_INSTRUCTIONS[mnemonic] = obj


def match_instruction(statement: List[Token]):
    # Check if basic instruction
    instruction = BASIC_INSTRUCTIONS.get(statement[0].value, None)
    if not instruction:
        return None
    # Check if statement actually matches
    if not instruction.match(statement):
        return None

    # TODO: Psuedo instructions

