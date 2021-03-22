from .isa import ISA_fc
from peak import Peak, name_outputs, family_closure, Const, family

@family_closure(family)
def CPU_fc(family):

    isa = ISA_fc.Py

    Bit = family.Bit
    Word = family.BitVector[16]

    @family.assemble(locals(), globals())
    class CPU(Peak):
        def __init__(self):
            self.flag = family.gen_register(Bit, 0)()

        @name_outputs(out=Word, pc_next=Word)
        def __call__(self,
                     inst: isa.Opcode,
                     a: Word,
                     b: Word,
                     pc: Word) -> Word:

            if inst == isa.NOR:
                out = ~(a | b)
                flag_next = out == 0
            else:
                out = 0
                flag_next = 0

            flag = self.flag(flag_next, family.Bit(1))
            if inst == isa.JMP:
                if flag:
                    pc_next = a
                else:
                    pc_next = b
            else:
                pc_next = pc+4

            return out, pc_next

    return CPU

@family_closure(family)
def CPU_mappable_fc(family):
    CPU = CPU_fc(family)
    Word = family.BitVector[16]
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class CPU_mappable(Peak):
        def __init__(self):
            self.cpu = CPU()

        @name_outputs(pc_next=isa.Word, val_out=isa.Word, flag_next=isa.Bit)
        def __call__(self,
                     inst: Const(isa.Opcode),
                     a: isa.Word,
                     b: isa.Word,
                     flag_init: isa.Bit,
                     pc: isa.Word,

                     ) -> (isa.DWord, isa.Word, isa.DWord):
            self.cpu.flag(flag_init, family.Bit(1))
            val_out, pc_next = self.cpu(inst, pc)
            return pc_next, val_out, self.cpu.flag(family.Bit(0), family.Bit(0))

        def _set_rs1_(self, rs1):
            self.cpu.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.cpu.register_file._set_rs2_(rs2)

    return CPU_mappable
