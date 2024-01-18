from pyssembler.architecture.mips.common.hardware import MIPSRegister, MIPSRegisterFile, constants


class MIPS32Register(MIPSRegister):
    def __init__(
            self,
            address: int,
            name: str,
            **kwargs
    ) -> None:
        super().__init__(address, name, constants.MIPSMemorySize.WORD, **kwargs)


class GeneralPurposeRegisters(MIPSRegisterFile):
    def __init__(self):
        super().__init__('General Purpose Registers')
        self._init_registers()

    def _init_registers(self) -> None:
        self.add_register(MIPS32Register(0, '$zero', read_only=True))
        self.add_register(MIPS32Register(1, '$at'))
        self.add_register(MIPS32Register(2, '$v0'))
        self.add_register(MIPS32Register(3, '$v1'))
        self.add_register(MIPS32Register(4, '$a0'))
        self.add_register(MIPS32Register(5, '$a1'))
        self.add_register(MIPS32Register(6, '$a2'))
        self.add_register(MIPS32Register(7, '$a3'))
        self.add_register(MIPS32Register(8, '$t0'))
        self.add_register(MIPS32Register(9, '$t1'))
        self.add_register(MIPS32Register(10, '$t2'))
        self.add_register(MIPS32Register(11, '$t3'))
        self.add_register(MIPS32Register(12, '$t4'))
        self.add_register(MIPS32Register(13, '$t5'))
        self.add_register(MIPS32Register(14, '$t6'))
        self.add_register(MIPS32Register(15, '$t7'))
        self.add_register(MIPS32Register(16, '$s0'))
        self.add_register(MIPS32Register(17, '$s1'))
        self.add_register(MIPS32Register(18, '$s2'))
        self.add_register(MIPS32Register(19, '$s3'))
        self.add_register(MIPS32Register(20, '$s4'))
        self.add_register(MIPS32Register(21, '$s5'))
        self.add_register(MIPS32Register(22, '$s6'))
        self.add_register(MIPS32Register(23, '$s7'))
        self.add_register(MIPS32Register(24, '$t8'))
        self.add_register(MIPS32Register(25, '$t9'))
        self.add_register(MIPS32Register(26, '$k0'))
        self.add_register(MIPS32Register(27, '$k1'))
        self.add_register(MIPS32Register(28, '$gp'))
        self.add_register(MIPS32Register(29, '$sp'))
        self.add_register(MIPS32Register(30, '$fp'))
        self.add_register(MIPS32Register(31, '$ra'))


class FloatingPointRegisters(MIPSRegisterFile):
    def __init__(self):
        super().__init__('Floating Point Registers')
        self._init_registers()

    def _init_registers(self) -> None:
        for i in range(32):
            self.add_register(MIPS32Register(i, f'$f{i}'))
