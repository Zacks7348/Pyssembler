from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from Pyssembler.mips.hardware import memory, MemorySegment


class SegmentTable(QTableWidget):
    def __init__(self, header, parent=None):
        super().__init__(parent)
        self.header = header
        h = self.horizontalHeader()
        h.setVisible(False)
        h.setStretchLastSection(True)
        v = self.verticalHeader()
        v.setVisible(False)
        v.setDefaultSectionSize(14)
        self.reset_table()

    def reset_table(self):
        self.clearContents()
        self.setRowCount(1)
        self.setColumnCount(len(self.header))
        for col, item in enumerate(self.header):
            item = QTableWidgetItem(str(item))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.setItem(0, col, item)

    def add_row(self, *args):
        self.setRowCount(self.rowCount()+1)
        for col, item in enumerate(args):
            item = QTableWidgetItem(str(item))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.setItem(self.rowCount()-1, col, item)


class TextSegmentWindow(SegmentTable):
    def __init__(self, parent=None):
        super().__init__(['Address', 'Encoding', 'Source', 'Assembly'], parent)

    def load_program(self, program):
        """
        Loads an assembled MIPSProgram object into the table
        """
        self.reset_table()
        instrs = sorted(
            [line for line in program.program_lines if line.memory_addr],
            key=lambda p: p.memory_addr)
        for instr in instrs:
            self.add_row(f'0x{instr.memory_addr:08x}', f'0x{instr.binary_instr:08x}',
                         instr.clean_line, instr.assembly)


class DataSegmentWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.shown_segments = set([seg for seg in MemorySegment])
        self.fmt = {hex: '0x{:08x}', int: '{}'}
        self.addr_radix = hex
        self.val_radix = hex

        self.mem_table = SegmentTable(
            ['Address', 'Value (+0)', 'Value (+1)',
             'Value (+2)', 'Value (+3)', 'Word Value'], parent)
        self.mem_table.reset_table()
        layout = QVBoxLayout()
        layout.addWidget(self.mem_table)
        opt_layout = QHBoxLayout()
        self.text_seg = QCheckBox('Text Segment')
        self.text_seg.setChecked(True)
        self.text_seg.stateChanged.connect(self.on_text_check)
        self.ktext_seg = QCheckBox('KText Segment')
        self.ktext_seg.setChecked(True)
        self.ktext_seg.stateChanged.connect(self.on_ktext_check)
        self.data_seg = QCheckBox('Data Segment')
        self.data_seg.setChecked(True)
        self.data_seg.stateChanged.connect(self.on_data_check)
        self.kdata_seg = QCheckBox('KData Segment')
        self.kdata_seg.setChecked(True)
        self.kdata_seg.stateChanged.connect(self.on_kdata_check)
        self.ext_seg = QCheckBox('Extern Segment')
        self.ext_seg.setChecked(True)
        self.ext_seg.stateChanged.connect(self.on_extern_check)
        self.mmio_seg = QCheckBox('MMIO Segment')
        self.mmio_seg.setChecked(True)
        self.mmio_seg.stateChanged.connect(self.on_mmio_check)

        self.hex_addr = QCheckBox('Hexadecimal Addresses')
        self.hex_addr.setChecked(True)
        self.hex_addr.stateChanged.connect(self.on_addr_hex_check)
        self.hex_vals = QCheckBox('Hexadecimal Values')
        self.hex_vals.setChecked(True)
        self.hex_vals.stateChanged.connect(self.on_val_hex_check)
        for segments in ((self.text_seg, self.ktext_seg), (self.data_seg, self.kdata_seg), (self.ext_seg, self.mmio_seg), (self.hex_addr, self.hex_vals)):
            col = QVBoxLayout()
            for seg in segments:
                col.addWidget(seg)
            opt_layout.addLayout(col)
        layout.addLayout(opt_layout)
        self.setLayout(layout)

    def load_memory(self):
        self.mem_table.reset_table()
        mem = memory.dump(radix=self.val_radix)
        for seg in mem.keys():
            if seg in self.shown_segments:
                for addr in sorted(mem[seg].keys()):
                    vals = mem[seg][addr]
                    self.mem_table.add_row(
                        self.fmt[self.addr_radix].format(addr), 
                        vals[0], vals[1], vals[2], vals[3], 
                        self.fmt[self.val_radix].format(memory.read_word(addr)))

    def on_check(self, state, seg):
        if state == Qt.Checked:
            self.shown_segments.add(seg)
        else:
            self.shown_segments.remove(seg)
        self.load_memory()

    def on_text_check(self, state):
        self.on_check(state, MemorySegment.TEXT)

    def on_ktext_check(self, state):
        self.on_check(state, MemorySegment.KTEXT)

    def on_data_check(self, state):
        self.on_check(state, MemorySegment.DATA)

    def on_kdata_check(self, state):
        self.on_check(state, MemorySegment.KDATA)

    def on_extern_check(self, state):
        self.on_check(state, MemorySegment.EXTERN)

    def on_mmio_check(self, state):
        self.on_check(state, MemorySegment.MMIO)
    
    def on_addr_hex_check(self, state):
        if state == Qt.Checked:
            self.addr_radix = hex
        else:
            self.addr_radix = int
        self.load_memory()
    
    def on_val_hex_check(self, state):
        if state == Qt.Checked:
            self.val_radix = hex
        else:
            self.val_radix = int
        self.load_memory()

    """
    TODO:
    1. Write logic for checkboxes
    2. Add Ascii view mode
    3. Add extra column to show word value?
    4. Displays labels here or in mem_table or new tab
    5. Set up event logic for listening to memory updates
    """
