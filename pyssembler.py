"""
This is the main script of this program.
"""

import logging
import argparse

from Pyssembler import run_application


def setup_logging(logger_name: str, output_file: str = None, debug: bool = False):
    """
    GUI application will use this logging object to log to console
    """
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    if output_file:
        # filename = "Pyssembler/logs/pyssembler-{}.log".format(datetime.now().strftime("%y-%m-%d-%M-%S"))
        handler = logging.FileHandler(filename=output_file, encoding='UTF-8', mode='w')
        handler.setFormatter(formatter)
        log.addHandler(handler)
    return log


def setup_parser():
    parser = argparse.ArgumentParser(description='Pyssembler - A MIPS32 IDE & Simulator')
    parser.add_argument('-m', '--main', type=str, help='The main MIPS32 assembly file, simulation starts at this file')
    parser.add_argument('-f', '--files', nargs='+', type=str, help='Additional MIPS32 assembly files')
    parser.add_argument('-l', '--log-file', type=str, help='Output file to save logs to')
    parser.add_argument('-o', '--output-file', type=str, help='Output file to save MIPS output to')
    parser.add_argument('-d', '--debug', action='store_true', help='Show debug logs')
    parser.add_argument('-s', '--step', action='store_true', help='Run the simulator in step mode')
    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()
    log = setup_logging('Pyssembler', output_file=args.output_file, debug=args.debug)
    if not args.main:
        # Run in GUI mode
        log.info('Running in GUI mode...')
        run_application()
    else:
        log.info('Running in terminal mode...')
        log.warning('Terminal mode not implemented!')


if __name__ == '__main__':
    main()
