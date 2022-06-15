"""
This file contains some useful data structures for working with MIPS
"""

from enum import Enum


__all__ = ['Segment']


class Segment(Enum):
    DATA = 0
    TEXT = 1
    KDATA = 2
    KTEXT = 3
