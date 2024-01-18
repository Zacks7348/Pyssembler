"""Main script of the pyssembler project

TODO: NOT IMPLEMENTED. USING AS TEST DRIVER
"""
from pathlib import Path

from pyssembler.architecture.core import AssemblyFile
from pyssembler.architecture.mips.mips32 import MIPS32CPU
from pyssembler.architecture.mips.common.mips_program import MIPSProgram


def main():
    cpu = MIPS32CPU(delay_slots=True)
    program = MIPSProgram(
        src_files=[
            AssemblyFile(Path(__file__).parent / 'pyssembler' / 'work' / 'mips_test.asm')
        ]
    )

    cpu.load_program_to_memory(program)
    cpu.execute()

    x=1


if __name__ == '__main__':
    main()
