from types import SimpleNamespace

from hwtypes.adt import Enum, Product, Sum, TaggedUnion

from peak import family_closure

from . import family


@family_closure(family)
def ISA_fc(family):

    Bit = family.Bit
    BitVector = family.BitVector
    Idx = family.Idx
    Word = family.Word
    DWord = family.DWord

    class Reg16(Product):
        idx = Idx

    class Reg32(Product):
        idx = Idx

    class Opcode(Enum):
        ADD = Enum.Auto()
        SUB = Enum.Auto()
        AND = Enum.Auto()
        OR = Enum.Auto()

    ADD = Opcode.ADD
    SUB = Opcode.SUB
    AND = Opcode.AND
    OR  = Opcode.OR

    class I16(Product):
        rd  = Reg16
        rs1 = Reg16
        imm = Word

    class R16(Product):
        rd  = Reg16
        rs1 = Reg16
        rs2 = Reg16

    class I32(Product):
        rd  = Reg32
        rs1 = Reg32
        imm = Word

    class R32(Product):
        rd  = Reg32
        rs1 = Reg32
        rs2 = Reg32


    Layout = Sum[I32, R32, I16, R16]

    class Inst(Product):
        data = Layout
        tag = Opcode

    AX  = Reg16(Idx(0))
    EAX = Reg32(Idx(0))
    BX  = Reg16(Idx(1))
    EBX = Reg32(Idx(1))
    CX  = Reg16(Idx(2))
    ECX = Reg32(Idx(2))
    DX  = Reg16(Idx(3))
    EDX = Reg32(Idx(3))

    return SimpleNamespace(**locals())
