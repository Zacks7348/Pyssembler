from typing import Dict


class State:
    """
    Represents the state of a MIPSEngine at the end of an execution cycle.

    States, when initially created, will only contain a diff compared to
    the previous state.
    """
    def __init__(self, prev_state=None):
        self.prev_state: 'State' = prev_state
        self.next_state: 'State' = None
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

    def last_register_value(self, register_name: str) -> int:
        if register_name in self.registers:
            return self.registers[register_name]

        if self.prev_state is not None:
            return self.prev_state.last_register_value(register_name)

        raise ValueError(f'No register found with name {register_name}')

    def last_memory_value(self, address: int) -> int:
        if address in self.memory:
            return self.memory[address]

        if self.prev_state is None:
            return 0

        return self.prev_state.last_memory_value(address)
