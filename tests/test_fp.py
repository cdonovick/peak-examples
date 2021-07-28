from examples.fp.sim import CPU_fc
from examples.fp.isa import ISA_fc

def test_py():
    CPU = CPU_fc.Py
    isa = ISA_fc.Py

    cpu = CPU()

    inst = isa.FP_ADD

    a = isa.Word(0)
    b = isa.Word(0)

    assert cpu(inst, a, b) == isa.Word(0)
