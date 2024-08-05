import functools
import inspect
from timeit import timeit
from collections import defaultdict
from functools import wraps, partial
from textwrap import dedent
import time
from typing import *

from .exceptions import *
from .program import SourceLine
from .simulator import CPUType, PyssemblerSimulatorBase
from pyssembler.utils import is_inside_class, extract_arguments_from_func, numeric

P = ParamSpec('P')
GroupT = TypeVar('GroupT', bound='Binding')
_DebugFuncT = Callable[Concatenate[GroupT, P], bool]


class PyssemblerDebugException(Exception):
    pass


class PyssemblerInvalidDebugCommand(PyssemblerDebugException):
    pass


def debugger_command(names: str, description: str, category: str = 'Pyssembler Debugger Commands'):
    def decorator(func: _DebugFuncT) -> _DebugFuncT:
        cmd = PyssemblerCLIDebuggerCommand(names, func, description, category)
        func.__pyssembler_debug_cmd__ = cmd
        return func

    return decorator


class PyssemblerCLIDebuggerCommand:
    def __init__(self, names: str, func: _DebugFuncT, description: str, category: str):
        self.names: str = names
        self.all_names: set[str] = set()
        self.description: str = description
        self.category: str = category
        self.parameters: list[str] = []
        self.binding: Optional[GroupT] = None

        self._parse_names(self.names)
        self._parse_parameters(func)

    @property
    def syntax(self) -> str:
        return f'{self.names} {" ".join(self.parameters)}'

    def _parse_names(self, names: str, prefix: str = ''):
        """
        :param names:
        :param prefix:
        :return:
        """
        try:
            name, rest = names.split('(', 1)
        except ValueError:
            name = names
            rest = ''

        if not rest and prefix and not name.endswith(')'):
            raise ValueError(f'Invalid name format: "{self.names}"')

        name = name.replace(')', '')

        for part in name.split('|'):
            cmd_name = f'{prefix}{part}'
            if cmd_name in self.all_names:
                raise ValueError(f'Invalid name format: "{self.names}"')

            self.all_names.add(cmd_name)
            if rest:
                self._parse_names(rest, prefix=cmd_name)

    def _parse_parameters(self, func: _DebugFuncT):
        for parameter in extract_arguments_from_func(func):
            if parameter.kind == parameter.KEYWORD_ONLY:
                self.parameters.append(f'[{parameter.name} ...]')

            else:
                self.parameters.append(f'[{parameter.name}]')


class PyssemblerCLISimulatorBase(PyssemblerSimulatorBase[CPUType]):
    """CLI-Implementation of the Pyssembler Simulator.

    This class provides general logic for simulating and debugging a PyssemblerCPU.
    Architectures should extend this to provide specific implementation details.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build a mapping of debugger commands
        self._debug_cmd_map: dict[str, _DebugFuncT] = {}
        self._debug_cmds: dict[str, list[_DebugFuncT]] = defaultdict(list)
        for member, value in inspect.getmembers(self):
            if inspect.ismethod(value) and hasattr(value.__func__, '__pyssembler_debug_cmd__'):
                cmd = value.__func__.__pyssembler_debug_cmd__
                self._debug_cmds[cmd.category].append(value)
                for name in cmd.all_names:
                    if name in self._debug_cmd_map:
                        raise KeyError(f'Debug command already exists with name "{name}"!')
                    self._debug_cmd_map[name] = value

    def _debugger(self):
        """Start the CLI Debugger.

        Control is given to the user via an interactive prompt.
        """
        statement = self._cpu.get_current_statement()
        if statement is None:
            statement = 'UNDEFINED'
        self._log.info(f'Current statement: {statement}')

        # Keep looping until the user runs a command that returns control
        # back to the simulated CPU (i.e. returns True)
        while True:
            # Since logging is setup as a glorified print() call
            # we can use input normally.
            cmd = input('>>> ').lower().strip()

            if not cmd:
                self._help_cmd()

            if self._invoke_debug_cmd(cmd):
                # Return control to the CPU
                return

    def _invoke_debug_cmd(self, cmd: str):
        if not cmd:
            return self._help_cmd()

        parts = cmd.split()
        cmd_name = parts[0]

        cmd_callback = self._debug_cmd_map.get(cmd_name, None)
        if cmd_callback is None:
            print(f'Unknown command "{cmd_name}"')
            return self._help_cmd()

        try:
            return cmd_callback(*parts[1:])

        except TypeError:
            print(f'Invalid usage for "{cmd_callback.__func__.__pyssembler_debug_cmd__.syntax}"')

        except Exception:
            return self._help_cmd()

    @debugger_command('b(reak)', 'Set a breakpoint')
    def _breakpoint_cmd(self, filename: str, lineno: str):
        lineno = numeric.from_string(lineno)
        for asm_file in self._cpu.get_current_program().src_files:
            if str(asm_file.path) == filename or asm_file.name == filename:
                src = asm_file.get_source_line(lineno-1)
                if src is not None:
                    self.set_breakpoint(src)
                    return False

    @debugger_command('h(elp)', 'Help Command')
    def _help_cmd(self) -> bool:
        help_str = ''
        for category, cmds in sorted(self._debug_cmds.items(), key=lambda x: x[0]):
            help_str += f'{category}\n'
            for cmd in sorted(cmds, key=lambda c: c.__func__.__pyssembler_debug_cmd__.names):
                cmd_obj = cmd.__func__.__pyssembler_debug_cmd__
                help_str += f'    {cmd_obj.syntax}\n        {cmd_obj.description}\n\n'

        print(help_str)
        return False

    @debugger_command('i(nfo)', 'List all breakpoints')
    def _info_cmd(self) -> bool:
        bstr = ''
        for breakpoint in self._breakpoints:
            bstr += f'{breakpoint.src_file}:{breakpoint.src_line}\n'

        self._log.info(f'Breakpoints:\n{bstr}')
        return False

    @debugger_command('q(uit)', 'Quit from the debugger. The program being executed is aborted.')
    def _quit_cmd(self) -> bool:
        raise ProgramStopped('User Quit')

    @debugger_command('s(tep)', 'Step to the next instruction.')
    def _step_cmd(self) -> bool:
        self.do_stepping(True)
        return True

    @debugger_command('c(ont(inue))', 'Continue program execution.')
    def _continue_cmd(self) -> bool:
        self.do_stepping(False)
        return True

    @debugger_command('src|source', 'Print the source of the current line.')
    def _source_cmd(self):
        statement = self._cpu.get_current_statement()
        addr = self._cpu.get_current_statement_address()
        if statement is None:
            self._log.info('UNDEFINED')

        else:
            self._log.info(
                f'{statement} ({statement.tokens[0].src_file.name}:{statement.tokens[0].src_line}, Memory Address 0x{addr})')
        return False

    @debugger_command('program', 'Print information about the current program')
    def _program_cmd(self) -> bool:
        program = self._cpu.get_current_program()
        if program is not None:
            res = f'Program:\nMain:\n  {program.main_file.path}\n\nAdditional files:\n'

            for asm_file in program.src_files:
                if asm_file == program.main_file:
                    continue

                res += f'  {asm_file.path}\n'

            print(res)

        return False

    def _handle_user_commands(self, cmd: str):
        """Interactive prompt.

        Commands that return control back to the CPU should return True.

        Returning False will keep the interactive prompt open.
        """
        self._stepping = False
        if cmd in ('h', 'help'):
            self._print_help()
            return False

        if cmd in ('info',):
            self._info_cmd()
            return False

        elif cmd in ('q', 'quit'):
            raise ProgramStopped('User Quit')

        elif cmd in ('s', 'step'):
            # Enable stepping and run the next statement
            self.do_stepping(True)

        elif cmd in ('c', 'cont', 'continue'):
            # Disable stepping and run the next statement
            self.do_stepping(False)

        elif cmd in ('src', 'source'):
            statement = self._cpu.get_current_statement()
            addr = self._cpu.get_current_statement_address()
            if statement is None:
                self._log.info('UNDEFINED')

            else:
                self._log.info(
                    f'{statement} ({statement.tokens[0].src_file.name}:{statement.tokens[0].src_line}, Memory Address 0x{addr})')

            return False

        else:
            self._print_help(f'Unknown command "{cmd}"')
            return False

        return True

    def _print_help(self, fail_reason: str = ''):
        self._log.info(self._generate_print_string(fail_reason))

    def _generate_print_string(self, fail_reason: str = ''):
        return dedent(
            f'''
                {fail_reason}
                Pyssembler Debugger Commands
                    h(elp)
                        Print the list of available commands.
                        
                    info
                        List all breakpoints
                        
                    q(uit)
                        Quit from the debugger. The program being executed is aborted.
                        
                    s(step)
                        Step to the next instruction.
                        
                    c(ont(inue))
                        Continue program execution.
                        
                    s(rc|ource)
                        Print the source of the current line.
                '''
        )
