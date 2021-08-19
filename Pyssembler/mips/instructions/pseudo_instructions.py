from Pyssembler.mips.hardware import registers
import json
import os.path

from ..tokenizer import tokenize_line, tokenize_instr_format, TokenType
from ..mips_program import ProgramLine
from ..errors import AssemblerError

__PSEUDO_INSTRS_FILE__ = os.path.dirname(__file__)+'/pseudo_instructions.json'


class PseudoInstruction:
    """
    Base class for supported MIPS32 pseudo instructions
    """

    def __init__(self, format_: str, expanded_instrs: list) -> None:
        self.format = format_
        
        self.mnemonic = self.format.split()[0]
        self.expanded_instructions = expanded_instrs

    def match(self, line: ProgramLine) -> list:
        """
        Returns True if the line is of this pseudo instruction type
        """
        pseudo_fmt_tokens = tokenize_instr_format(self.format)
        if line.tokens[0].value != self.mnemonic:
            return False
        #import pdb; pdb.set_trace()
        if len(line.tokens) != len(pseudo_fmt_tokens)+1:
            # Number of tokens should match
            return False
        for i, token in enumerate(line.tokens[1:]):
            if token.type != pseudo_fmt_tokens[i].type:
                return False
        return True

    def expand(self, line: ProgramLine) -> list:
        """Expand the pseudo instruction into MIPS32 Instructions

        Returns
        -------
        list
            The list of expanded instructions
        """

        expanded = []
        pseudo_fmt_tokens = tokenize_instr_format(self.format)
        #import pdb; pdb.set_trace()
        for i, token in enumerate(line.tokens[1:]):
            # Verify that the pseudo instruction is formatted properly
            if token.type == TokenType.COMMENT:
                break
            if token.type != pseudo_fmt_tokens[i].type:
                raise AssemblerError(
                    filename=line.filename,
                    linenum=line.linenum,
                    charnum=token.charnum,
                    message='Invalid Syntax: Expected {}'.format(pseudo_fmt_tokens[i].type.name))
            if token.type == TokenType.REGISTER:
                # The value will have been converted to the register address, need to keep name for now
                token.value = registers.get_name_from_address(token.value)
        for expanded_instr in self.expanded_instructions:
            exp_tokens = tokenize_instr_format(expanded_instr)
            for i, token in enumerate(pseudo_fmt_tokens, start=1):
                expanded_instr = expanded_instr.replace(
                    token.value, str(line.tokens[i].value))
            expanded.append(expanded_instr)
        return expanded

    def __str__(self) -> str:
        return 'MIPS32 PSEUDO INSTRUCTION '+self.mnemonic

    def __repr__(self) -> str:
        return 'MIPS32 INSTRUCTION: mnemonic={}, formatting={}, expand={}'.format(self.mnemonic, self.format,
                                                                                  self.expanded_instructions)


def get_pseudo_instructions():
    output = []
    with open(__PSEUDO_INSTRS_FILE__, 'r') as f:
        for pseudo_instr, expanded_instrs in json.load(f).items():
            output.append(PseudoInstruction(pseudo_instr, expanded_instrs))
    return output
