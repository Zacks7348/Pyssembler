"""Main driver of the Pyssembler CLI Application"""
import argparse
import logging
from pathlib import Path

from pyssembler import PYSSEMBLER_ROOT_LOGGER
from pyssembler.utils import PrintHandler
from pyssembler.languages.mips.common.mips_cli_simulator import MIPSCLISimulator
from pyssembler.core.architecture import AssemblyFile, SourceLine
from pyssembler.languages.mips.mips32.architecture import MIPS32CPU
from pyssembler.languages.mips.common.architecture.mips_program import MIPSProgram


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('asm_files', nargs='+', type=Path, help='ASM files to be ran')
    parser.add_argument('-e', '--exception-handler', type=Path, help='Exception Handler')
    parser.add_argument('--delay-slots', action='store_true', help='Simulate delay slots')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging')

    return parser.parse_args()


def _init_logging(debug: bool):
    sh = PrintHandler()
    sh.setLevel(logging.DEBUG if debug else logging.INFO)
    PYSSEMBLER_ROOT_LOGGER.addHandler(sh)


def _main():
    args = _get_args()
    _init_logging(debug=args.verbose)

    cpu = MIPS32CPU(delay_slots=args.delay_slots)
    program = MIPSProgram(src_files=[AssemblyFile(asm) for asm in args.asm_files])
    cpu.load_program_to_memory(program)

    runner = MIPSCLISimulator(cpu, debug=args.debug)

    runner.run()


if __name__ == '__main__':
    _main()
