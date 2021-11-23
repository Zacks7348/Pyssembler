import json
import unittest

from Pyssembler.mips.instructions import instruction_set as instr_set
from Pyssembler.mips.mips_program import MIPSProgram
from Pyssembler.mips.tokenizer import tokenize_program
from Pyssembler.mips.errors import TokenizationError
from Pyssembler import Assembler
from Pyssembler.mips.hardware import GPR, CP0, Integer


# class IntegerTests(unittest.TestCase):
#     def test_set_bit0(self):
#         self.assertEqual(1, Integer.set_bit(0b000, 0))

#     def test_set_bit1(self):
#         self.assertEqual(2, Integer.set_bit(0b000, 1))

#     def test_clear_bit0(self):
#         self.assertEqual(6, Integer.clear_bit(0b111, 0))

#     def test_clear_bit1(self):
#         self.assertEqual(5, Integer.clear_bit(0b111, 1))

#     def test_write_bits(self):
#         self.assertEqual(0b01010,
#                          Integer.change_bits(0b00000, 1, 3, 0b101))

class RegisterTests(unittest.TestCase):
    def test_gpr_signed_op(self):
        for name in GPR.reg_names:
            GPR.write(name, -100)
            self.assertTrue(GPR.read(name, signed=True), -100)

    def test_gpr_unsigned_op(self):
        for name in GPR.reg_names:
            GPR.write(name, 100)
            self.assertTrue(GPR.read(name, signed=True), 100)

    def test_cp0_signed_op(self):
        for name in CP0.reg_names:
            CP0.write(name, -100)
            self.assertTrue(CP0.read(name, -100))

    def test_cp0_unsigned_op(self):
        for name in CP0.reg_names:
            CP0.write(name, 100)
            self.assertTrue(CP0.read(name, 100))
    
    def test_cp0_status_write(self):
        CP0.write(CP0.STATUS, 0)
        CP0.write_status(int_mask=0x000000FF, user_mode=1, exc_lvl=1, int_enable=1)
        self.assertEqual(0x0000FF13, CP0.read(CP0.STATUS))


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

# class TokenizerTests(unittest.TestCase):
#     def test_loop_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/loop.asm')
#         tokenize_program(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_edgetest_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/edgetest.asm')
#         tokenize_program(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_pseudo_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/pseudo.asm')
#         tokenize_program(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_fail_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/fail.asm')
#         with self.assertRaises(TokenizationError):
#             tokenize_program(p)

# class AssemblerTests(unittest.TestCase):
#     def setUp(self):
#         self.a = Assembler()

#     def test_loop_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/loop.asm')
#         self.a.assemble(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_edgetest_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/edgetest.asm')
#         self.a.assemble(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_pseudo_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/pseudo.asm')
#         self.a.assemble(p)
#         self.assertTrue(len(p.program_lines) > 0)

#     def test_fail_asm(self):
#         p = MIPSProgram(main='Pyssembler/work/fail.asm')
#         with self.assertRaises(TokenizationError):
#             self.a.assemble(p)


if __name__ == '__main__':
    unittest.main()
