from utils import int2bin
from utils import BIT, BYTE, HWORD, WORD
import json

MEMORY_CONFIG_FILE = 'Simulator/memory_config.json'


class Memory:
    """
    Represents Pyssembler memory. Inspired by SPIM and MIPS

    Implemented memory as a dictionary rather than singular list. 
    Assume all valid memory addresses that aren't keys in the dictionary
    point to trash (initial values are 0).

    All addresses must be word-aligned.

    All values are stored in memory in little-endian order.

    """
    def __init__(self) -> None:

        # Declare different segments of memory
        self.config = {}
        with open(MEMORY_CONFIG_FILE, 'r') as f:
            self.config = json.load(f)

        # MIPS32 uses 32-bit addresses for memory
        # Memory is broken up into the following sections:
        
        # memory mapped I/O section
        self.mmio_base_addr = int(self.config['MMIO base address'], 16)
        self.mmio_limit_addr = int(self.config['MMIO limit address'], 16)
        # kernel data section
        self.kdata_base_addr = int(self.config['kdata base address'], 16)
        self.kdata_limit_addr = int(self.config['kdata limit address'], 16)
        # kernel text section
        self.ktext_base_addr = int(self.config['ktext base address'], 16)
        self.ktext_limit_addr = int(self.config['ktext limit address'], 16)
        # stack section
        self.stack_base_addr = int(self.config['stack base address'], 16)
        # user text section
        self.text_base_addr = int(self.config['text base address'], 16)
        self.text_limit_addr = int(self.config['text limit address'], 16)
        # part of user data section reserved for .extern symbols
        self.extern_base_addr = int(self.config['extern base address'], 16)
        self.extern_limit_addr = int(self.config['extern limit address'], 16)
        # user data section
        self.data_base_addr = int(self.config['data base address'], 16)
        # starting heap address 
        self.heap_base_addr = int(self.config['heap base address'], 16)
        self.heap_pointer = self.heap_base_addr
        # boundary between stack and heap
        self.stack_heap_boundary = int(self.config['stack-heap boundary'], 16)
        # max address user can write to in memory
        self.user_memory_limit = int(self.config['user memory limit'], 16)
        # max memory address
        self.memory_limit = int(self.config['memory limit'], 16)
        # starting address for $gp
        self.global_pointer = int(self.config['global pointer'], 16)       

        self.memory = {}
    
    def read(self, addr: int, data_size: int) -> str:
        """
        Returns the value at the given address in memory

        If the address hasn't been initialized yet, return 0
        """
        if addr % (WORD / data_size) != 0:
            # if addr is not word-aligned
            raise ValueError('Memory Address is not aligned')

        if not 0 < addr < self.user_memory_limit:
            # If addr not in memory range
            raise ValueError('Invalid Memory Address')
        
        if data_size != WORD or data_size != HWORD or data_size != BYTE:
            raise ValueError('data_size must be {}, {}, or {}'.format(WORD, HWORD, BYTE))
        
        if self.in_data_range(addr) or self.in_text_range(addr):
            # In data or text segment, read one byte at a time
            return self._read_bytes(addr, data_size)

        if self.in_stack_range(addr):
            return self._read_bytes(addr-(data_size // BYTE)+1, data_size)

    def _read_bytes(self, addr: int, data_size: int) -> str:
        val = ''
        for offset in range(data_size // BYTE):
            val += self.memory.get(addr+offset, '00000')
        return val

    def write(self, addr: int, val: str) -> None:
        """
        Writes a binary value into memory starting at addr. 
        Value must be of size byte, hword, or word
        """
        SIZE = len(val)
        if SIZE != WORD and SIZE != HWORD and SIZE != BYTE:
            raise ValueError('value must be of size WORD, HWORD, OR BYTE. Got {} bits'.format(SIZE))
        if (SIZE == WORD and (addr % (WORD // BYTE)) != 0) or \
            (SIZE == HWORD and (addr % (HWORD // BYTE)) != 0):
            # if addr is not aligned
            raise ValueError('address is not aligned! {}')

        if not 0 < addr < self.user_memory_limit:
            # If addr not in memory range
            raise ValueError('Invalid Memory Address {}'.format(hex(addr)))
            
        if self.in_data_range(addr) or self.in_text_range(addr):
            # In data or text segment, write one byte at a time ignoring boundaries
            val_bytes = []
            for i in range(BYTE, len(val)+1, BYTE):
                val_bytes.append(val[i-BYTE:i])
            self._write_bytes(addr, val_bytes)
        
        if self.in_stack_range(addr):
            # In stack, same as data write except stack grows downwards
            val_bytes = []
            for i in range(BYTE, len(val)+1, BYTE):
                val_bytes.append(val[i-BYTE:i])
            self._write_bytes(addr-len(val_bytes)+1, val_bytes)

    
    def _write_bytes(self, addr: int, val_bytes: list) -> None:
        """
        Helper function for writing bytes to memory

        Starting at addr, write each byte sequentially
        """
        for offset, byte in enumerate(val_bytes):
            write_addr = addr+offset
            if write_addr >= self.memory_limit:
                raise IndexError('Trying to write past memory limit')
            self.memory[addr+offset] = byte
        

    def allocate_bytes_in_heap(self, num_bytes: int) -> int:
        """
        Returns address of next word-aligned heap address
 
        if num_bytes is not word aligned, allocates additional bytes to
        make num_bytes word aligned

        In worst case scenario where 3 bytes are allocated and unused for
        each allocation call, heap becomes very fragmented and wastefull
        """
        address = self.heap_pointer
        while (num_bytes//4 != 0): num_bytes += 1

        self.heap_pointer += num_bytes


    def get_modified_addresses(self) -> list:
        return list(self.memory.keys())

    def in_user_memory(self, addr: int) -> bool:
        return self.text_base_addr <= addr < self.ktext_base_addr

    def in_MMIO_range(self, addr: int) -> bool:
        return self.mmio_base_addr <= addr < self.mmio_limit_addr

    def in_kdata_range(self, addr: int) -> bool:
        return self.kdata_base_addr <= addr < self.kdata_limit_addr

    def in_ktext_range(self, addr: int) -> bool:
        return self.ktext_base_addr <= addr < self.ktext_limit_addr

    def in_stack_range(self, addr: int) -> bool:
        return self.stack_base_addr >= addr > self.stack_heap_boundary

    def in_text_range(self, addr: int) -> bool:
        return self.text_base_addr <= addr < self.text_limit_addr

    def in_extern_range(self, addr: int) -> bool:
        return self.extern_base_addr <= addr < self.extern_limit_addr

    def in_data_range(self, addr: int) -> bool:
        return self.data_base_addr <= addr < self.stack_heap_boundary

        
if __name__ == '__main__':
    mem = Memory()
    mem.write(0x7fffeffc-173016, '00000000111111110000000011111111')
    print(0x7fffeffc-173016)
    print(mem.memory)
    print(mem.get_modified_addresses())
