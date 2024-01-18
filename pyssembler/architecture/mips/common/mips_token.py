from .mips_enums import MIPSTokenType
from pyssembler.architecture.core.token import Token


class MIPSToken(Token[MIPSTokenType]):

    def __str__(self):
        return f'Token(raw={self.raw_value},value={self.value},type={self.type.name})'
