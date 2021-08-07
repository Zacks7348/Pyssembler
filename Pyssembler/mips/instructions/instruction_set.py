from typing import Union
from enum import Enum

from .instructions import Instruction, get_instructions
from .. import utils

__INSTRUCTIONS__ = get_instructions()

def get_instruction_names(sort: bool = False) -> list:
    """
    Returns a list of implemented instruction mnemonics

    Parameters
    ----------
    sort : bool, optional
        Declare that the list should be sorted alphabetically
    """

    output = []
    for instr in __INSTRUCTIONS__:
        output.append(instr.mnemonic)
    if sort:
        return sorted(output)
    return output

def get_instruction(mnemonic: str) -> Instruction:
    """
    Returns the instruction object of the mnemonic

    This function utilizes the lru_cache from functools
    to avoid searching for commonly searched mnemonics

    Parameters
    ----------
    mnemonic : str
        The name of the instruction

    Returns
    -------
    Instruction
        The Instruction object of the mnemonic or None if doesn't exist
    """

    for instr in __INSTRUCTIONS__:
        if instr.mnemonic == mnemonic:
            return instr
    return None

def is_instruction(mnemonic: str) -> bool:
    """
    Returns true if the mnemonic passed is an implemented instruction

    Shortcut for using get_instruction and testing for None

    Parameters
    ----------
    mnemonic : str
        The name of the instruction
    """
    return not get_instruction(mnemonic) is None

def match_binary_instruction(bin_instr: int) -> Instruction:
    """
    Tries to match a binary instruction to an instruction object

    Parameters
    ----------
    bin_instr : int
        The binary instruction

    Returns
    -------
    Instruction
        The instruction object that matches the binary instruction or None if
        no match exists
    """

    for instr in __INSTRUCTIONS__:
        if instr.match(bin_instr):
            return instr
    return None

def encode_instruction(line, bstring=False) -> Union[int, str]:
    """
    Encode the passed program line into binary

    This function serves as a shortcut for mapping a mnemonic to an instruction object then 
    calling the instruction's encode() function

    Assumes the line has already been tokenized

    Parameters
    ----------
    statement : ProgramStatement
        The statement to be encoded
    bstring : bool
        If true, return the encoded instruction as a binary string
    """

    # print('Attempting to Encode {}...'.format(line.tokens[0].value))
    instr_obj = get_instruction(line.tokens[0].value)
    if instr_obj is None:
        # print('\tCould not find instruction object')
        return None
    print('[INSTR_SET] Encoding {} with obj {}'.format(line, instr_obj))
    return instr_obj.encode(line, bstring)

    



