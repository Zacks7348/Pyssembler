import json
import os.path

from ..utils import BIT, BYTE, HWORD, WORD
from ..utils import WORD_LENGTH_BYTES, HWORD_LENGTH_BYTES
from ..utils import MAX_UINT32, MIN_SINT32

MEMORY_CONFIG_FILE = os.path.dirname(__file__)+'/../memory_config.json'


class Memory:
    """
    Represents Pyssembler memory. Inspired by SPIM and MIPS

    Implemented memory as a dictionary rather than singular list. 
    Assume all valid memory addresses that aren't keys in the dictionary
    point to trash (initial values are 0).

    All addresses must be word-aligned.

    All values are stored in memory in little-endian order.

    Needs the CP0 object created in the simulator object for determining if
    in user or kernel mode
    """
    def __init__(self, CP0) -> None:

        self.CP0 = CP0 #Coprosser 0

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
    
    def read_word(self, addr: int) -> int:
        """
        Read a word from memory starting at addr
        """
        if addr % WORD_LENGTH_BYTES != 0:
            raise ValueError('Address is not naturally aligned')
        mask = 0xFF000000
        val = 0 & mask
        if self.in_stack_segment(addr):
            addr = addr - WORD_LENGTH_BYTES + 1
        for i, val_byte in enumerate(self._read_bytes(addr, WORD_LENGTH_BYTES)):
            val = ((val_byte << WORD-(i*BYTE)-BYTE) & (mask >> i*BYTE)) | val
        return val
    
    def read_hword(self, addr: int) -> int:
        """
        Read a half word from memory starting at addr
        """
        if addr % HWORD_LENGTH_BYTES != 0:
            raise ValueError('Address is not naturally aligned')
        mask = 0x0000FF00
        val = 0 & mask
        if self.in_stack_segment(addr):
            addr = addr - HWORD_LENGTH_BYTES + 1
        for i, val_byte in enumerate(self._read_bytes(addr, HWORD_LENGTH_BYTES)):
            val = ((val_byte << HWORD-(i*BYTE)-BYTE) & (mask >> i*BYTE)) | val
        return val
    
    def read_byte(self, addr: int) -> int:
        """
        Read a byte from memory starting at addr
        """
        return self.memory.get(addr, 0)

    def _read_bytes(self, addr: int, num_bytes: int) -> list:
        """
        Reads bytes from memory starting at addr

        Returns list of bytes in order of read
        """
        val_bytes = []
        for i in range(num_bytes):
            val_bytes.append(self.memory.get(addr+i, 0))
        return val_bytes
    
    def write(self, addr: int, val: int, size: int) -> None:
        """
        Writes a value into simulated memory starting at addr
        addr must be naturally aligned with size
        """
        if not size in (WORD, HWORD, BYTE):
            raise ValueError('Value must be of size WORD, HWOWRD or BYTE')
        if (addr % (size // BYTE)) != 0:
            raise ValueError('Address is not naturally aligned')
        if not 0 <= addr <= MAX_UINT32:
            raise ValueError('Address out of bounds')
        if self.CP0.user_mode == 1:
            # user mode
            if not self.in_user_memory(addr):
                raise ValueError('Cannot write to kernel memory in user mode')
        masks = {WORD: 0xFF000000, HWORD: 0x0000FF00, BYTE: 0x000000FF}

        val_bytes = []
        for i in range(0, size, BYTE):
            val_bytes.append((val & (masks[size] >> i)) >> size-i-BYTE)

        if self.in_stack_segment(addr):
            self._write_bytes(addr-len(val_bytes)+1, val_bytes)
        else:
            self._write_bytes(addr, val_bytes)
        
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
        """
        address = self.heap_pointer
        while ((num_bytes-1)//4 != 0): num_bytes += 1

        self.heap_pointer += num_bytes
        return address


    def get_modified_addresses(self) -> list:
        return list(self.memory.keys())
    
    def dump(self, radix=int) -> dict:
        """
        Dumps memory
        """
        formatting = {int: '{}', hex: '0x{:02x}', bin: '{:08b}'}
        dumped = {}
        for addr in self.memory:
            if addr % 4 == 0:  
                dumped[addr] = []
                for i in range(4):
                    val = formatting[radix].format(self.memory.get(addr+i, 0), 2)
                    dumped[addr].append(val)
        return dumped

    # Helper functions for determining which memory segment an address is in
    def in_user_memory(self, addr: int) -> bool:
        return self.text_base_addr <= addr < self.ktext_base_addr

    def in_MMIO_segment(self, addr: int) -> bool:
        return self.mmio_base_addr <= addr < self.mmio_limit_addr

    def in_kdata_segment(self, addr: int) -> bool:
        return self.kdata_base_addr <= addr < self.kdata_limit_addr

    def in_ktext_segment(self, addr: int) -> bool:
        return self.ktext_base_addr <= addr < self.ktext_limit_addr

    def in_stack_segment(self, addr: int) -> bool:
        return self.stack_base_addr >= addr > self.stack_heap_boundary

    def in_text_segment(self, addr: int) -> bool:
        return self.text_base_addr <= addr < self.text_limit_addr

    def in_extern_segment(self, addr: int) -> bool:
        return self.extern_base_addr <= addr < self.extern_limit_addr

    def in_data_segment(self, addr: int) -> bool:
        return self.data_base_addr <= addr < self.stack_heap_boundary

