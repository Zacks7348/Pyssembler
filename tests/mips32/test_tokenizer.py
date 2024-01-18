import unittest

from pyssembler.architecture.mips.common.mips_enums import MIPSTokenType
from pyssembler.architecture.mips.mips32 import MIPS32CPU
from pyssembler.architecture.core.token import Token


class TestMIPS32Tokenizer(unittest.TestCase):
    def setUp(self) -> None:
        self.cpu: MIPS32CPU = MIPS32CPU()

    def test_basic_instruction_tokenization(self):
        text = 'add $t1, $t1, $t1'
        tokenized_statements = self.cpu.assembler.tokenize_text(
            text,
            line_start=0,
            char_start=0,
            asm_file=None,
            ignore_comments=False,
            ignore_whitespace=True,
        )

        self.assertEquals(len(tokenized_statements), 1)
        generated_statement = tokenized_statements[0]
        expected_statement = [
            Token
        ]
