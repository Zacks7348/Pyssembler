import json
from os import name
import os.path
import ast

from ..hardware import registers, memory
from .errors import *


class Simulator:
    """
    Base Class for MIPS32 Simulators

    Provides all core components of a MIPS simulator. Also provides a function
    to assemble mips instructions
    """

    def __init__(self, step=False) -> None:

        # If step=True, wait for user input before executing next instr
        self.step = step



    