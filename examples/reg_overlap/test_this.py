from .sim import CPU_fc, CPU_mappable_fc
from .isa import  ISA_fc

def test_py():
    CPU = CPU_fc.Py
    isa = ISA_fc.Py

    cpu = CPU()


    cpu.register_file.store(isa.EAX.idx, isa.DWord(0))
    cpu.register_file.store(isa.EBX.idx, isa.DWord(0))
    cpu.register_file.store(isa.ECX.idx, isa.DWord(0))
    cpu.register_file.store(isa.EDX.idx, isa.DWord(0))

    pc = isa.DWord(0)

    # Store -1 to AX
    inst = isa.Inst(
        data=isa.Layout(isa.I16(
            rd=isa.AX,
            rs1=isa.AX,
            imm=isa.Word(-1)
        )),
        tag=isa.ADD,
    )
    pc = cpu(inst, pc)

    assert cpu.register_file.load1(isa.EAX.idx) == isa.Word(-1).zext(16)

    # Add 1 to EAX
    inst = isa.Inst(
        data=isa.Layout(isa.I32(
            rd=isa.EAX,
            rs1=isa.EAX,
            imm=isa.Word(1)
        )),
        tag=isa.ADD,
    )

    pc = cpu(inst, pc)
    assert cpu.register_file.load1(isa.EAX.idx) == (1 << isa.Word.size)

    # Move AX to BX
    inst = isa.Inst(
        data=isa.Layout(isa.I16(
            rd=isa.BX,
            rs1=isa.AX,
            imm=isa.Word(0)
        )),
        tag=isa.ADD,
    )
    pc = cpu(inst, pc)
    assert cpu.register_file.load1(isa.EBX.idx) == 0

    #Move EAX to EBX
    inst = isa.Inst(
        data=isa.Layout(isa.I32(
            rd=isa.EBX,
            rs1=isa.EAX,
            imm=isa.Word(0)
        )),
        tag=isa.ADD,
    )
    pc = cpu(inst, pc)
    assert cpu.register_file.load1(isa.EBX.idx) == (1 << isa.Word.size)


def test_smt():
    CPU = CPU_fc.SMT
    cpu = CPU()
