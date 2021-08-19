from Pyssembler.mips import instructions
from Pyssembler.mips.instructions import instruction_set as instr_set
from Pyssembler.mips.mips_program import MIPSProgram, ProgramLine
from Pyssembler.mips.assembler import Assembler, Segment

def validate_instr_generation():
    print('Validating instructions...')
    failed = []
    with open('test.txt', 'w') as f:
        pass_test = True
        instr_list = instr_set.get_basic_instruction_mnemonics(sort=True)
        for i, name in enumerate(instr_list):
            print('Validating {}...'.format(name))
            f.write('Testing {} instruction...\n'.format(name))
            instr = instr_set.get_basic_instruction(name)
            test_instr = instr.generate_example(bstring=True)
            mask = '{:032b}'.format(instr.mask)
            val = '{:032b}'.format(instr.match_value)
            f.write('\t{:<15} {:<32}\n'.format('encoding', instr.encoding))
            f.write('\t{:<15} {}\n'.format('test instr', test_instr))
            f.write('\t{:<15} {:<32}\n'.format('mask', mask))
            f.write('\t{:<15} {:<32}\n'.format('match val', val))
            match = instr_set.match_binary_instruction(int(test_instr, 2))
            f.write('\tINFO: bin_len={}, match=({})\n'.format(len(test_instr), match))
            if len(test_instr) != 32: 
                pass_test = False
                #print('{} bad length'.format(name))
            elif match is None: 
                pass_test = False
                #print('{} bad match (None)'.format(name))
            elif match.mnemonic != name: 
                pass_test = False
                #print('{} bad match'.format(name))
            
            if pass_test:
                f.write('TEST RESULT: PASS\n\n')
            else: 
                f.write('TEST RESULT: FAIL\n\n')
                failed.append(name)
            print('Validated {}/{}'.format(i+1, len(instr_list)))
        f.write('-----FAILED-----\n')
        for name in failed:
            f.write('{}\n'.format(name))

def validate_encodings():
    failed = []
    print('Validating encodings...')
    program = MIPSProgram(main='test.asm')
    asm = Assembler()
    asm.assemble(program)
    ENCODINGS = []
    with open('encodings.txt') as f:
        ENCODINGS = f.readlines()
    instructions = asm.segment_contents[Segment.TEXT]

    if len(ENCODINGS) != len(instructions):
        print('NOT ALL INSTRUCTIONS ENCODED')
        return

    statement: ProgramLine = None
    for statement, encoding in zip(instructions, ENCODINGS):
        encoding = encoding.strip()
        print('\t Testing {}'.format(statement))
        print('\t Expected Encoding:', encoding)
        enc_str = '{:032b}'.format(statement.binary_instr)
        print('\t Encoded instr:    ', enc_str)
        res = encoding == enc_str
        if res: print('Encoding Result: PASS')
        else: 
            print('Encoding Result: FAIL')
            failed.append(statement)

    print('-----FAILED-----')
    for statement in failed:
        print(repr(statement))

