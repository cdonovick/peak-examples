from types import SimpleNamespace

from hwtypes.adt import Enum, Product, TaggedUnion, Sum

from peak import family_closure

from . import family
from . import sizes


@family_closure(family)
def ISA_fc(family):

    Bit = family.Bit
    BitVector = family.BitVector

    Idx = BitVector[sizes.IdxLen]
    Word = BitVector[sizes.WordLen]
    Shift = BitVector[sizes.ShiftLen]
    Const = BitVector[sizes.ConstLen]

    # LAYOUTS:
    # R : | op 6 | rs 5 | rt 5 | rd 5 | sa 5 | funct 6 |
    # I : | op 6 | rs 5 | rt 5 | imm 16                |
    # J : | op 6 | address 26                          |

    # r-type instuctions that operate on 1 registers
    class TF(Enum):
        T = Enum.Auto()
        F = Enum.Auto()

    class LOHI(Enum):
        LO = Enum.Auto()
        HI = Enum.Auto()

    class R1Inst(Product):
        dir = TF
        reg = LOHI

    class R1(Product):
        rd = Idx
        op = R1Inst

    # r-type instuctions that operate on 2 registers
    class R2Inst(Enum):
        # Arith
        CLO = Enum.Auto()
        CLZ = Enum.Auto()
        SEB = Enum.Auto()
        SEH = Enum.Auto()

        #Logic
        WSBH = Enum.Auto()

        # Mul / Div
        DIV = Enum.Auto()
        DIVU = Enum.Auto()
        MADD = Enum.Auto()
        MADDU = Enum.Auto()
        MSUB = Enum.Auto()
        MSUBU = Enum.Auto()
        MULT = Enum.Auto()
        MULTU = Enum.Auto()

    class R2(Product):
        rd = Idx
        rs = Idx
        op = R2Inst

    #Instructions that operate on 3 registers
    class R3Inst(Enum):
        # Arith
        # ADD - Traps
        ADDU = Enum.Auto()
        # SUB - Traps
        SUBU = Enum.Auto()

        # Shifts
        ROTRV = Enum.Auto()
        SLLV = Enum.Auto()
        SRAV = Enum.Auto()
        SRLV = Enum.Auto()

        # Logic
        AND = Enum.Auto()
        NOR = Enum.Auto()
        OR  = Enum.Auto()
        XOR = Enum.Auto()

        # Conditions
        MOVN = Enum.Auto()
        MOVZ = Enum.Auto()
        SLT = Enum.Auto()
        SLTU = Enum.Auto()

        # Mul / Div
        MUL = Enum.Auto()


    class R3(Product):
        rd = Idx
        rs = Idx
        rt = Idx
        op = R3Inst

    # r-type instuctions that operate on 2 registers and 5 bit const
    class RsInst(Enum):
        ROTR = Enum.Auto()
        SLL = Enum.Auto()
        SRA = Enum.Auto()
        SRL = Enum.Auto()

    class Rs(Product):
        rd = Idx
        rs = Idx
        sa = Shift
        op = RsInst

    # r-type instuctions that operate on 2 registers and 2 5 bit consts
    class RlmInst(Enum):
        EXT = Enum.Auto()
        INS = Enum.Auto()

    class Rlm(Product):
        rd = Idx
        rs = Idx
        mb = Shift
        lb = Shift
        op = RlmInst


    # I-type instuctions that operate on 2 registers
    class I2Inst(Enum):
        # Arith
        # ADDI - Traps
        ADDIU = Enum.Auto()

        # Logical
        ANDI = Enum.Auto()
        ORI = Enum.Auto()
        XORI = Enum.Auto()

        # Conditions
        SLTI = Enum.Auto()
        SLTIU = Enum.Auto()

    class I2(Product):
        rd = Idx
        rs = Idx
        im = Const
        op = I2Inst

    class LUI(Product):
        rd = Idx
        im = Const

    Inst = Sum[R1, R2, R3, Rs, Rlm, I2, LUI]

    return SimpleNamespace(**locals())
