from .symbol_table import SymbolTable
from .instructions import instruction_set as instr_set
from .directives import *
from .hardware import *
from . import tokenizer

# Populate keywords in tokenizer
# tokenizer.register_keywords(instr_set.BASIC_INSTRUCTIONS, tokenizer.TokenType.MNEMONIC)
# tokenizer.register_keywords(DIRECTIVES, tokenizer.TokenType.DIRECTIVE)
# tokenizer.register_keywords(REGISTERS, tokenizer.TokenType.REGISTER)
