from types import SimpleNamespace

from hwtypes.adt import Enum, Product, Sum, TaggedUnion

from peak import family_closure, family

@family_closure(family)
def ISA_fc(family):

    Bit = family.Bit
    BitVector = family.BitVector
    Word = BitVector[16]

    class Inst(Enum):
        AND = Enum.Auto()
        INV = Enum.Auto()
        FP_ADD = Enum.Auto()

    AND = Inst.AND
    INV = Inst.INV
    FP_ADD = Inst.FP_ADD
    return SimpleNamespace(**locals())

