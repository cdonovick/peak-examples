from .sim import CPU_fc, CPU_mappable_fc
from .isa import ISA_fc

def test_py():
    CPU = CPU_fc.Py
    isa = ISA_fc.Py

    cpu = CPU()

    a = isa.Word(0)
    b = ~a

    pc_init = isa.Word(0)

    out, pc = cpu(isa.NOR, a, a, pc_init)

    assert pc == pc_init + 4
    assert out == isa.Word(-1)

    out, pc = cpu(isa.JMP, a, b, pc)

    assert pc == b
    assert out == 0

    out, pc = cpu(isa.NOR, a, b, pc)

    assert pc == b + 4
    assert out == 0

    out, pc = cpu(isa.JMP, a, b, pc)

    assert pc == a
    assert out == 0


def test_smt():
    CPU = CPU_fc.SMT
    cpu = CPU()


