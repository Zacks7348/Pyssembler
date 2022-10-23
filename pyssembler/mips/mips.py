"""
This file contains some useful data structures for working with MIPS
"""

from enum import Enum


class Segment(Enum):
    DATA = 0
    TEXT = 1
    KDATA = 2
    KTEXT = 3
