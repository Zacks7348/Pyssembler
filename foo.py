from Pyssembler.mips.hardware import memory, MemorySize

if __name__ == '__main__':
    memory.set_verbose(2)
    memory.write(0, 200, MemorySize.BYTE)
    print(memory.dump(radix=bin))
    print(memory.read_byte(0, signed=False))