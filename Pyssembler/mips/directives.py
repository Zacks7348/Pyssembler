from enum import Enum

class DirectiveInfo:
    def __init__(self, directive, format_, description) -> None:
        self.directive = directive
        self.format = format_
        self.description = description

class Directives:
    INCLUDE = '.include'
    GLOBL = '.globl'
    EXTERN = '.extern'
    SPACE = '.space'
    ALIGN = '.align'
    WORD = '.word'
    HALF = '.half'
    BYTE = '.byte'
    ASCII = '.ascii'
    ASCIIZ = '.asciiz'
    TEXT = '.text'
    KTEXT = '.ktext'
    DATA = '.data'
    KDATA = '.kdata'
    DIRECTIVES = {
        INCLUDE: DirectiveInfo('.align', '.align immediate',
                               'Align the next data item on a byte boundary (0=byte, 1=halfword, 2=word)'),
        ASCII: DirectiveInfo('.ascii', 'label: .ascii "string"',
                             'Store the string in memory without a null terminator'),
        ASCIIZ: DirectiveInfo('.asciiz', 'label: .asciiz "string"',
                              'Store the string in memory with a null terminator'),
        BYTE: DirectiveInfo('.byte', 'label: .byte immediate',
                            'Store the listed value(s) as 8 bit bytes'),
        DATA: DirectiveInfo('.data', '.data',
                            'Declare that the following lines are stored in Data segment'),
        EXTERN: DirectiveInfo('.extern', '.extern label immediate',
                              'Declare the label and byte length as a global data field'),
        GLOBL: DirectiveInfo('.globl', '.globl label',
                             'Declare the label(s) as global to allow other files to reference them'),
        HALF: DirectiveInfo('.half', 'label: .half immediate',
                            'Store the listed value(s) as 16 bit halfwords (with natural alignment)'),
        INCLUDE: DirectiveInfo('.include', '.include filename',
                               'Insert the contents of a file starting at location of the directive'),
        KDATA: DirectiveInfo('.kdata', '.kdata',
                             'Declare that the following lines are stored in Kernel Data segment'),
        KTEXT: DirectiveInfo('.ktext', '.ktext',
                             'Declare that the following lines are stored in Kernel Text segment'),
        SPACE: DirectiveInfo('.space', 'label: .space immediate',
                             'Declare the label and byte length as a local data field'),
        TEXT: DirectiveInfo('.text', '.text',
                            'Declare that the following lines are stored in Text segment'),
        WORD: DirectiveInfo('.word', 'label: .word immediate',
                            'Store the listed value(s) as 32 bit words (with natural alignment)')
    }

    @staticmethod
    def is_directive(token: str) -> bool:
        return token in Directives.DIRECTIVES

    @staticmethod
    def get_directives() -> list:
        return list(Directives.DIRECTIVES.keys())

    @staticmethod
    def get_format(directive: str) -> str:
        return Directives.DIRECTIVES[directive].format

    @staticmethod
    def get_description(directive: str) -> str:
        return Directives.DIRECTIVES[directive].description