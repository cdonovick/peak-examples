from types import SimpleNamespace

from hwtypes.adt import Enum, Product

from peak import family_closure

from . import family
from . import sizes
from . import isa as isa_

# Micro code
@family_closure(family)
def Micro_fc(family):
    isa = isa_.ISA_fc(family)



    class ShifterControl(Product):
        a = isa.Word
        b = isa.Shift
        inst = isa.RsInst

    class ALUOp(Enum):
        AND = Enum.Auto()
        OR = Enum.Auto()
        XOR = Enum.Auto()
        ADD = Enum.Auto()
        MUL = Enum.Auto()
        DIV = Enum.Auto()
        # could definitely do this by resuing the other instructions
        # putting flags in the second output.  I am lazy and it doesn't
        # matter
        LT  = Enum.Auto()
        # Should put shifts in the own unit but whatever
        SHL = Enum.Auto()
        SHR = Enum.Auto()
        ROT = Enum.Auto()
        MOV = Enum.Auto()

    class ALUControl(Product):
        signed = isa.Bit
        alu_op = ALUOp
        inv_lu_out = isa.Bit

    return SimpleNamespace(**locals())
