import typing

from pyssembler.architecture.mips.common.instruction import MIPSBasicInstruction
from pyssembler.architecture.core import PyssemblerInstructionSet

__all__ = [
    'MIPS32InstructionSet',
    'yield_basic_instr_cls',
    'mips32_instruction'
]

_INSTR = typing.Type[MIPSBasicInstruction]

_basic_instruction_cls_list: typing.List[_INSTR] = []


class MIPS32InstructionSet(PyssemblerInstructionSet[MIPSBasicInstruction]):
    pass


def yield_basic_instr_cls() -> typing.Iterable[_INSTR]:
    yield from _basic_instruction_cls_list


def mips32_instruction(
        instr: _INSTR = None
) -> typing.Union[_INSTR, typing.Callable[[_INSTR], _INSTR]]:
    def inner(i: _INSTR) -> _INSTR:
        _basic_instruction_cls_list.append(i)
        return i

    # Called with parenthesis
    if instr is None:
        return inner

    # Called without parenthesis
    else:
        return inner(instr)
