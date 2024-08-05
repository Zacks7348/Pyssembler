from textwrap import dedent

from .architecture.cpu import MIPSCPU
from pyssembler.core.architecture.cli_simulator import PyssemblerCLISimulatorBase, debugger_command
from pyssembler.utils import numeric
from pyssembler.languages.mips.common.architecture.assembler_errors import MIPSAssemblerError
from pyssembler.languages.mips.common.architecture.mips_exceptions import MIPSException


class MIPSCLISimulator(PyssemblerCLISimulatorBase[MIPSCPU]):
    @debugger_command('wpc', 'Update the Program Counter.', 'MIPS Debugger Commands')
    def _wpc_cmd(self, value: str) -> bool:
        pass

    def _handle_user_commands(self, cmd: str):
        if cmd in ('ppc',):
            val = self._cpu.pc.read_integer()
            self._log.info(f'{self._cpu.pc.names[0]}: {val} (0x{val:08x})')
            return False

        if cmd.startswith('wpc'):
            self._wpc(cmd)
            return False

        if cmd.startswith('pgpr'):
            self._pgpr(cmd)
            return False

        if cmd.startswith('pmem'):
            self._pmem(cmd)
            return False

        if cmd in ('symbols',):
            self._symbols()
            return False

        if cmd.startswith('eval'):
            self._eval(cmd)
            return False

        return super()._handle_user_commands(cmd)

    def _wpc(self, cmd: str):
        parts = cmd.split(' ')
        if len(parts) != 2:
            self._print_help('Invalid usage for "wpc"!')
            return

        try:
            value = numeric.from_string(parts[-1])
            self._cpu.pc.write_integer(value)
        except Exception as e:
            self._log.error(f'Something went wrong updating the Program Counter: {e}')
            return

    def _pgpr(self, cmd: str):
        parts = cmd.split(' ')
        if len(parts) == 1:
            registers = list(iter(self._cpu.gpr))

        elif len(parts) == 2:
            value = parts[-1].strip()
            try:
                registers = [self._cpu.gpr.get_register(addr=int(value))]

            except ValueError:
                try:
                    registers = [self._cpu.gpr.get_register(name=value)]

                except ValueError:
                    self._log.error(f'Unknown GPR "{value}"!')
                    return

        else:
            self._print_help('Invalid usage for "pgpr"!')
            return

        register_str = ''
        for i, register in enumerate(registers, start=1):
            reg_val = register.read_integer(signed=False)
            end = ', ' if i % 4 != 0 else '\n'
            register_str += f'{register.names[0]}: {reg_val} (0x{reg_val:08x}){end}'

        self._log.info(f'\n{register_str}')

    def _pmem(self, cmd):
        try:
            _, addr, n_bytes = cmd.split(' ')
            addr = numeric.from_string(addr)
            n_bytes = numeric.from_string(n_bytes)
        except Exception:
            self._print_help('Invalid usage for "pmem"!')
            return

        value = self._cpu.memory.read_bytes(int(addr), int(n_bytes))
        self._log.info(f'{value} (0x{value:08x})')

    def _symbols(self):
        program = self._cpu.get_current_program()
        asm_file = self._cpu.get_current_file()

        symbols_str = ''
        # Global symbols first
        if program.global_symbols:
            symbols_str += f'\nGlobal Symbols:\n{program.global_symbols.tabulate()}\n\n'

        try:
            local_symbols = program.get_file_symbols(asm_file)
            if local_symbols:
                symbols_str += f'{asm_file.name} Symbols:\n{local_symbols.tabulate()}'
        except Exception:
            pass

        self._log.info(symbols_str)

    def _eval(self, cmd: str):
        try:
            _, instr_txt = cmd.split(' ', maxsplit=1)

        except Exception:
            self._print_help('Invalid usage for "eval"!')
            return

        asm_file = self._cpu.get_current_file()
        if asm_file is None:
            self._print_help('Not currently debugging a file!')

        try:
            statement = self._cpu.assembler.assemble_single_instruction(instr_txt, asm_file)

        except MIPSAssemblerError as e:
            self._log.error(f'Could not evaluate statement:\n{e}')
            return

        if statement.is_instruction():
            try:
                statement.execute()

            except MIPSException as e:
                self._log.error(f'Could not evaluate statement:\n{e}')

    def _generate_print_string(self, *args, **kwargs):
        return super()._generate_print_string(*args, **kwargs) + dedent(
            '''
            
            MIPS Debugger Commands
                ppc
                    Print the value contained in the Program Counter register.
                    
                wpc [value]
                    Update the Program Counter.
                
                pgpr [GPR Register ...]
                    Print the value contained in the General Purpose Register. 
                    If no register is provided then all registers are printed.
                    
                pmem [address] [bytes]
                    Print the value contained in simulated memory starting at
                    the specified address and reading n bytes. 
                    
                symbols
                    Display the symbol tables for this program.
                
                eval [statement]
                    Evaluate a statement. Include directives are not handled.
                
            '''
        )
