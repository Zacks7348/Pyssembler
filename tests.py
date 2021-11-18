import json
import unittest

from Pyssembler.mips.instructions import instruction_set as instr_set
from Pyssembler.mips.mips_program import MIPSProgram
from Pyssembler.mips.tokenizer import tokenize_program
from Pyssembler.mips.errors import TokenizationError


# class InstructionTests(unittest.TestCase):
#     def setUp(self):
#         with open('Pyssembler/mips/instructions/instructions.json', 'r') as f:
#             self.instrs = json.load(f)
#         with open('Pyssembler/mips/instructions/pseudo_instructions.json', 'r') as f:
#             self.pinstrs = json.load(f)

#     def test_instr_gen(self):
#         for mnemonic in self.instrs:
#             self.assertTrue(instr_set.is_mnemonic(mnemonic))

#     def test_pinstr_gen(self):
#         for instr in self.pinstrs:
#             self.assertTrue(instr_set.is_mnemonic(instr.split()[0]))

#     def test_get_basic_instructions(self):
#         self.assertTrue(
#             len(instr_set.get_basic_instruction_mnemonics()) == len(self.instrs))

#     def test_get_pseudo_instrs(self):
#         pinstrs = set([instr.split()[0] for instr in self.pinstrs])
#         self.assertTrue(len(instr_set.get_pseudo_instruction_mnemonics()) == len(pinstrs))

class TokenizerTests(unittest.TestCase):
    def test_loop_asm(self):
        p = MIPSProgram(main='Pyssembler/work/loop.asm')
        tokenize_program(p)
        self.assertTrue(len(p.program_lines) > 0)

    def test_edgetest_asm(self):
        p = MIPSProgram(main='Pyssembler/work/edgetest.asm')
        tokenize_program(p)
        self.assertTrue(len(p.program_lines) > 0)

    def test_pseudo_asm(self):
        p = MIPSProgram(main='Pyssembler/work/pseudo.asm')
        tokenize_program(p)
        self.assertTrue(len(p.program_lines) > 0)

    def test_fail_asm(self):
        p = MIPSProgram(main='Pyssembler/work/fail.asm')
        with self.assertRaises(TokenizationError):
            tokenize_program(p)


if __name__ == '__main__':
    unittest.main()
