import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QTabWidget, 
    QTableWidget,
    QTableWidgetItem, 
    QHBoxLayout, 
    QFileDialog,
    QVBoxLayout, 
    QWidget, 
    QSplitter)
from Pyssembler.mips.errors import TokenizationError

from Pyssembler.mips.hardware import GPR, CP0, MemorySegment
from Pyssembler.mips import Assembler, Simulator, MIPSProgram
from Pyssembler.mips import AssemblerError, AssemblerWarning
from .consoles import Consoles
from .segments import DataSegmentWindow, TextSegmentWindow

__LOGGER__ = logging.getLogger('Pyssembler.GUI')

class SimulatorWindow(QWidget):
    def __init__(self, consoles) -> None:
        super().__init__()
        self.consoles = consoles
        self.__init_ui()
        self.simulator = Simulator()
        self.assembler = Assembler()
        self.program = None

    def __init_ui(self):
        self.regs = RegisterTable(self)
        self.text = TextSegmentWindow()
        self.mem = DataSegmentWindow()

        self.main_tabs = QTabWidget(self)
        self.main_tabs.addTab(self.text, 'Text Segment')
        self.main_tabs.addTab(self.mem, 'Data Segment')
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.main_tabs)
        splitter.addWidget(self.regs)
        splitter.setSizes([500, 50])
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    
    def init_sim_env(self, main, files=None) -> bool:
        """
        Initialize the simulation environment for the specified program.

        First assembles the program. If any errors occure then stop and
        log error in pyssembler console.

        Initialize sim object

        Return False on error and return True if successfull
        """

        __LOGGER__.debug('Initializing simulation environment...')
        files = [] if not files else files
        __LOGGER__.debug('Creating MIPS32 program...')
        self.consoles.p_message('Assembling program...')
        self.consoles
        self.program = MIPSProgram(files, main=main)
        try:
            __LOGGER__.debug('Assembling program...')
            self.assembler.assemble(self.program)
        except AssemblerError as e:
            # An error occured during assembly, log error
            __LOGGER__.debug('Error occured during assembly!')
            self.consoles.p_message(str(e))
            return False
        except TokenizationError as e:
            # An error occured during tokenization, log error
            __LOGGER__.debug('Error occured during tokenization!')
            self.consoles.p_message(str(e))
            return False
        self.consoles.p_message('Successfully assembled program!')
        self.text.load_program(self.program)
        self.mem.load_memory()
        return True
        

class RegisterTable(QTabWidget):
    """
    Displays the current values of the MIPS registers
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.__init_gpr_table()
        self.__init_cp0_table()

    def __init_gpr_table(self):
        self.gpr_table = self.__create_table(34, 3)
        self.__add_item(self.gpr_table, 0, 0, 'Name')
        self.__add_item(self.gpr_table, 0, 1, 'Address')
        self.__add_item(self.gpr_table, 0, 2, 'Value')
        for i, (reg_name, reg_addr) in enumerate(GPR.reg_names.items(), start=1):
            self.__add_item(self.gpr_table, i, 0, reg_name)
            self.__add_item(self.gpr_table, i, 1, reg_addr)
            self.__add_item(self.gpr_table, i, 2, 0)
        self.__add_item(self.gpr_table, 33, 0, 'PC')
        self.__add_item(self.gpr_table, 33, 2, 0)
        self.addTab(self.gpr_table, 'GPR')
    
    def __init_cp0_table(self):
        self.cp0_table = self.__create_table(5, 3)
        self.__add_item(self.cp0_table, 0, 0, 'Name')
        self.__add_item(self.cp0_table, 0, 1, 'Address')
        self.__add_item(self.cp0_table, 0, 2, 'Value')
        for i, (reg_name, reg_addr) in enumerate(CP0.reg_names.items(), start=1):
            self.__add_item(self.cp0_table, i, 0, reg_name)
            self.__add_item(self.cp0_table, i, 1, reg_addr)
            self.__add_item(self.cp0_table, i, 2, 0)
        self.addTab(self.cp0_table, 'CP0')

    def __create_table(self, row_cnt, col_cnt):
        table = QTableWidget(self)
        table.setRowCount(row_cnt)
        table.setColumnCount(col_cnt)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(10)
        return table

    
    def __add_item(self, table: QTableWidget, row: int, col: int, item):
        item = QTableWidgetItem(str(item))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        table.setItem(row, col, item)