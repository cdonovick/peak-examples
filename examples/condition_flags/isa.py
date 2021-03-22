from types import SimpleNamespace

from hwtypes.adt import Enum, Product, Sum, TaggedUnion

from peak import family_closure, family

@family_closure(family)
def ISA_fc(family):

    Bit = family.Bit
    BitVector = family.BitVector
    Word = BitVector[16]

    class Opcode(Enum):
        NOR = Enum.Auto()
        JMP = Enum.Auto()


    NOR = Opcode.NOR
    JMP = Opcode.JMP

    return SimpleNamespace(**locals())

