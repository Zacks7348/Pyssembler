from typing import Dict


class State:
    """
    Represents the state of a MIPSEngine at the end of an execution cycle.

    States, when initially created, will only contain a diff compared to
    the previous state.
    """
    def __init__(self, prev_state=None):
        self.prev_state: 'State' = prev_state
        self.registers: Dict[str, int] = {}
        self.memory: Dict[int, int] = {}

    def resolve(self):
        """
        Resolves the current state.

        Forwards the last updates for each register/memory address
        up to this state.
        """

        state = self.prev_state
        while state is not None:
            for reg_name, reg_value in state.registers.items():
                if reg_name not in self.registers:
                    self.registers[reg_name] = reg_value

            for mem_addr, mem_value in state.memory.items():
                if mem_addr not in self.memory:
                    self.memory[mem_addr] = mem_value

            state = state.prev_state
