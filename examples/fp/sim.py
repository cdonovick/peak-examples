from .isa import ISA_fc
from peak import Peak, name_outputs, family_closure, Const, family
from peak.family import PyFamily, SMTFamily

from hwtypes import SMTFPVector, FPVector, RoundingMode

@family_closure(family)
def CPU_fc(family):

    isa = ISA_fc.Py

    Bit = family.Bit
    Word = family.BitVector[16]
    FPU = FPU_fc(family)

    @family.assemble(locals(), globals())
    class CPU(Peak):
        def __init__(self):
            self.fpu = FPU()

        @name_outputs(out=Word)
        def __call__(self,
                     inst: isa.Inst,
                     a: Word,
                     b: Word) -> Word:
            if inst == isa.AND:
                return a & b
            elif inst == isa.INV:
                return ~a
            else:
                return self.fpu(a, b)

    return CPU



@family_closure(family)
def FPU_fc(family):
    isa = ISA_fc.Py
    Word = family.BitVector[16]

    if isinstance(family, SMTFamily):
        FPV = SMTFPVector
    if isinstance(family, PyFamily):
        FPV = FPVector

    BFloat16 = FPV[8, 7, RoundingMode.RNE, False]

    @family.assemble(locals(), globals())
    class FPU(Peak):
        @name_outputs(out=Word)
        def __call__(self,
                     a: Word,
                     b: Word) -> Word:
            a = BFloat16.reinterpret_from_bv(a)
            b = BFloat16.reinterpret_from_bv(b)
            c = a + b
            return c.reinterpret_as_bv()

    return FPU
