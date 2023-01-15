"""
main script of the pyssembler project

engine = MIPSEngine(architecture=MIPS_32BIT, MIPS_64BIT)

engine.assemble

"""
import argparse
from pyssembler.mips.hardware import MIPSMemory, integer


def _get_args():
    parser = argparse.ArgumentParser('pyssembler')
    parser.add_argument('main', type=str, help='Main MIPS file')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logs')


def main():
    mem = MIPSMemory()

    mem.write_hword(0, 1)
    word = mem.read_word(0)

    print(word, bin(word))


if __name__ == '__main__':
    main()
