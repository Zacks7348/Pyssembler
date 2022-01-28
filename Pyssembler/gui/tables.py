from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget)

from Pyssembler.mips.hardware import MEM, MemorySegment, GPR, CP0


class DataTable(QTableWidget):
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
        self.mapping = {}
        self.highlight_brush = QBrush(QColor('yellow'))
        self.__highlighted = set()  # Saves row numbers that are highlighted

    def reset_table(self):
        self.clearContents()
        self.setRowCount(1)
        self.setColumnCount(len(self.header))
        for col, item in enumerate(self.header):
            item = QTableWidgetItem(str(item))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.setItem(0, col, item)

    def add_row(self, *args, map_=None):
        self.setRowCount(self.rowCount() + 1)
        for col, item in enumerate(args):
            self.__add_item(self.rowCount() - 1, col, item)
        if map_ is not None:
            self.mapping[map_] = self.rowCount() - 1
        return self.rowCount() - 1

    def update_row(self, row: int, *args, start=0):
        for col, item in enumerate(args, start=start):
            self.__add_item(row, col, item)

    def insert_row(self, row: int, *args):
        self.insertRow(row)
        for col, item in enumerate(args):
            self.__add_item(row, col, item)

    def highlight_row(self, row, clear=True):
        """
        Highlights a row. Clears all previous highlighting
        """
        if row == 0:
            # Don't allow highlighting header row
            return
        if row in self.__highlighted:
            # Row is already highlighted
            return
        if clear:
            for c_row in list(self.__highlighted):
                # Highlight with brush from item 0,0
                # Since we don't allow highlighting header row, this
                # will always be default
                self.__highlight_row(c_row, self.item(0, 0).background())
            self.__highlighted.clear()
        self.__highlight_row(row, self.highlight_brush)
        self.__highlighted.add(row)

    def __highlight_row(self, row: int, brush: QBrush):
        for col in range(self.columnCount()):
            self.item(row, col).setBackground(brush)

    def __add_item(self, row: int, col: int, val):
        item = QTableWidgetItem(str(val))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.setItem(row, col, item)

    def get_row_from_map(self, val):
        return self.mapping.get(val, None)

    @property
    def highlighted_rows(self):
        return self.__highlighted.copy()


class TextSegmentTable(DataTable):
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
                         instr.clean_line, instr.assembly, map_=instr.memory_addr)

    def update_highlight(self, pc):
        row = self.get_row_from_map(pc)
        if row is None:
            return
        self.highlight_row(row)


class DataSegmentTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.shown_segments = set([seg for seg in MemorySegment])
        self.fmt = {hex: '0x{:08x}', int: '{}'}
        self.addr_radix = hex
        self.val_radix = hex

        self.mem_table = DataTable(
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
        for segments in (
                (self.text_seg, self.ktext_seg), (self.data_seg, self.kdata_seg), (self.ext_seg, self.mmio_seg),
                (self.hex_addr, self.hex_vals)):
            col = QVBoxLayout()
            for seg in segments:
                col.addWidget(seg)
            opt_layout.addLayout(col)
        layout.addLayout(opt_layout)
        self.setLayout(layout)

    def load_memory(self):
        self.mem_table.reset_table()
        mem = MEM.dump(radix=self.val_radix)
        for seg in mem.keys():
            if seg in self.shown_segments:
                for addr in sorted(mem[seg].keys()):
                    vals = mem[seg][addr]
                    self.mem_table.add_row(
                        self.fmt[self.addr_radix].format(addr),
                        vals[0], vals[1], vals[2], vals[3],
                        self.fmt[self.val_radix].format(MEM.read_word(addr)))

    def update_val(self, addr: int, byte_vals, word_val):
        for row in range(1, self.mem_table.rowCount()):
            if self.mem_table.item(row, 0).text() == str(addr):
                # Update the row
                for col, byte in enumerate(byte_vals, start=1):
                    self.mem_table.item(row, col).setText(self.fmt[self.val_radix].format(byte))
                self.mem_table.item(row, 5).setText(self.fmt[self.val_radix].format(word_val))
                return
            base = 16 if self.addr_radix == hex else 10
            if int(self.mem_table.item(row, 0).text(), base) > addr:
                # Insert new row
                if MEM.get_segment(addr) in self.shown_segments:
                    self.mem_table.insert_row(
                        row,
                        self.fmt[self.addr_radix].format(addr),
                        self.fmt[self.val_radix].format(byte_vals[0]),
                        self.fmt[self.val_radix].format(byte_vals[1]),
                        self.fmt[self.val_radix].format(byte_vals[2]),
                        self.fmt[self.val_radix].format(byte_vals[3]),
                        self.fmt[self.val_radix].format(word_val)
                    )

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


class GPRTable(DataTable):
    def __init__(self, parent=None):
        super().__init__(['Name', 'Address', 'Value'], parent)

    def load_registers(self):
        self.reset_table()
        for reg_name, reg_addr in GPR.reg_names.items():
            self.add_row(reg_name, reg_addr, 0, map_=reg_addr)
        self.add_row('PC', None, 0, map_=32)

    def update_register(self, addr: int, val: int):
        row = self.get_row_from_map(addr)
        if row is None:
            return
        self.update_row(row, addr, val, start=1)
        if addr != 32:
            # Don't highlight PC since it always updates
            self.highlight_row(row)


class CP0Table(DataTable):
    def __init__(self, parent=None):
        super().__init__(['Name', 'Address', 'Value'], parent)

    def load_registers(self):
        self.reset_table()
        for reg_name, reg_addr in CP0.reg_names.items():
            self.add_row(reg_name, reg_addr, 0)


class RegisterTable(QTabWidget):
    """
    Displays the current values of the MIPS registers
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.gpr = GPRTable()
        self.cp0 = CP0Table()
        self.addTab(self.gpr, 'GPR')
        self.addTab(self.cp0, 'CP0')

    def load_registers(self):
        self.gpr.load_registers()
        self.cp0.load_registers()
