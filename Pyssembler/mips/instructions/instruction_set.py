from Pyssembler.mips.mips_program import ProgramLine
from typing import Union

from .instructions import BasicInstruction, PseudoInstruction
from .instructions import generate_basic_instructions, generate_pseudo_instructions

__BASIC_INSTRUCTIONS__ = generate_basic_instructions()
__BASIC_MNEMONICS__ = set(sorted([instr.mnemonic for instr in __BASIC_INSTRUCTIONS__]))
__PSEUDO_INSTRUCTIONS__ = generate_pseudo_instructions()
__PSEUDO_MNEMONICS__ = set(sorted([instr.mnemonic for instr in __PSEUDO_INSTRUCTIONS__]))


def get_basic_instruction_mnemonics() -> list:
    """
    Returns a list of implemented instruction mnemonics
    """

    return list(__BASIC_MNEMONICS__)


def get_pseudo_instruction_mnemonics() -> list:
    """
    Returns a list of implemented pseudo instruction mnemonics
    """
    
    return list(__PSEUDO_MNEMONICS__)

def get_basic_instruction(line: ProgramLine) -> BasicInstruction:
    """
    Returns the basic instruction object of the mnemonic

    Parameters
    ----------
    line : ProgramLine
        The ProgramLine object to get the basic instruction object of

    Returns
    -------
    BasicInstruction
        The BasicInstruction object that matches line or None if no match
    """

    for instr in __BASIC_INSTRUCTIONS__:
        if instr.match(line):
            return instr
    return None

def get_pseudo_instruction(line: ProgramLine) -> PseudoInstruction:
    """
    Returns the pseudo instruction object of the mnemonic

    Parameters
    ----------
    line : ProgramLine
        The ProgramLine object to get the pseudo instruction object of

    Returns
    -------
    PseudoInstruction
        The PseudoInstruction object that matches line or None if no match
    """
    for instr in __PSEUDO_INSTRUCTIONS__:
        if instr.match(line):
            return instr
    return None


def is_mnemonic(mnemonic: str) -> bool:
    """
    Returns True if the mnemonic passed is a valid basic instruction mnemonic
    or pseudo instruction mnemonic
    """

    return mnemonic in __BASIC_MNEMONICS__ or mnemonic in __PSEUDO_MNEMONICS__

def is_basic_instruction(line: ProgramLine) -> bool:
    """
    Returns true if the mnemonic passed is an implemented instruction

    Parameters
    ----------
    line : ProgramLine
        The ProgramLine object to test
    """
    return not get_basic_instruction(line) is None

def is_pseudo_instruction(line: ProgramLine) -> bool:
    """
    Returns true if the mnemonic passed is an implemented pseudo instruction

    Parameters
    ----------
    line : ProgramLine
        The ProgramLine object to test
    """

    return not get_pseudo_instruction(line) is None


def encode_instruction(line: ProgramLine, bstring=False) -> Union[int, str]:
    """
    Encode the passed program line into binary

    This function serves as a shortcut for mapping a mnemonic to an instruction object then 
    calling the instruction's encode() function

    Assumes the line has already been tokenized

    Parameters
    ----------
    line : ProgramStatement
        The line to be encoded
    bstring : bool
        If true, return the encoded instruction as a binary string
    """

    # print('Attempting to Encode {}...'.format(line.tokens[0].value))
    instr_obj = get_basic_instruction(line)
    if instr_obj is None:
        # print('\tCould not find instruction object')
        return None
    return instr_obj.encode(line, bstring)


def expand_pseudo_instruction(line: ProgramLine) -> list:
    """
    Expand the passed pseudo instruction into the equivalent 
    basic instruction(s)

    Parameters
    ----------
    line : ProgramLine
        The line to be expanded

    Returns
    -------
    list
        The list of expanded basic instructions as strings
    """
    instr_obj = get_pseudo_instruction(line)
    #print(line, repr(instr_obj))
    if instr_obj is None:
        return None
    return instr_obj.expand(line)


