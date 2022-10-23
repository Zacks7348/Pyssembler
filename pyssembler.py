"""
main script of the Pyssembler project

engine = MIPSEngine(architecture=MIPS_32BIT, MIPS_64BIT)

engine.assemble

"""
import argparse


def _get_args():
    parser = argparse.ArgumentParser('Pyssembler')
    parser.add_argument('main', type=str, help='Main MIPS file')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logs')


def main():
    pass


if __name__ == '__main__':
    main()
