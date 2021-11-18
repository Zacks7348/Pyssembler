"""
This is the console version of Pyssembler.

This version only provides simulation functionality.
"""
import argparse
import logging
import sys

from Pyssembler import MIPSProgram, Assembler, Simulator
from Pyssembler import AssemblerError, TokenizationError
import config


class LoggerNameFilter(logging.Filter):
    def filter(self, record):
        record.name = record.name.rsplit('.', 1)[-1]
        return True


LOGGER = logging.getLogger('PYSSEMBLER')


def setup_logging(debug, outfile=None):
    # Global root logger
    global LOGGER
    if debug:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)
    if outfile:
        handler = logging.FileHandler(
            filename=outfile, encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter(
            '[%(name)s][%(levelname)s] %(message)s'))
        handler.addFilter(LoggerNameFilter())
        LOGGER.addHandler(handler)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(name)s][%(levelname)s] %(message)s'))
    handler.addFilter(LoggerNameFilter())
    LOGGER.addHandler(handler)


def setup_parser():
    parser = argparse.ArgumentParser(
        description='Pyssembler: A lightweight MIPS32 Simulator')
    parser.add_argument(
        'main', type=str, help='The main MIPS ASM file, this is where simulation will start')
    parser.add_argument('-f', '--files', nargs='+',
                        type=str, help='Additional MIPS ASM files to be assembled')
    parser.add_argument('-d', '--debug',
                        action='store_true', help='Show debug logs')
    parser.add_argument('-l', '--log-file', type=str,
                        help='Output file to save logs to')
    parser.add_argument('-s', '--step', action='store_true',
                        help='Stop at each step of the simulator')
    parser.add_argument('-ss', '--show-state', action='store_true',
                        help='Display state of register file after each simulator step')
    return parser

def update_config(args: argparse.Namespace):
    config.set_debug(args.debug)
    config.set_log_file(args.log_file)

def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logging(args.debug, args.log_file)

    try:
        LOGGER.info('Creating MIPS program from passed ASM files...')
        program = MIPSProgram(main=args.main, src_files=args.files)
    except FileNotFoundError as e:
        LOGGER.error('File {} does not exist'.format(e.filename))
        sys.exit('Could not load asm files into program')

    LOGGER.info('Program created!')

    asm = Assembler()

    # If one of my custom exceptions gets raised during assembly,
    # Catch it and print out the exception since it will contain
    # usefull debugging information such as syntax errors
    try:
        LOGGER.info('Assembling program..')
        asm.assemble(program)
        LOGGER.info('Assembly complete!')
    except AssemblerError as e:
        LOGGER.error('Assembly failed')
        LOGGER.error(e)
        exit()
    except TokenizationError as e:
        LOGGER.error('Assembly failed')
        LOGGER.error(e)
        exit()

    sim = Simulator(step=args.step, states=args.show_state)
    LOGGER.info('Starting simulation...')
    sim.simulate()
    LOGGER.info('Simulation stopped')


if __name__ == '__main__':
    main()
