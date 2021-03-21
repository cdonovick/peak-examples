
from peak import Peak, name_outputs, family_closure, Const
from .isa import ISA_fc
from . import family
from hwtypes import modifiers

Initial = modifiers.make_modifier('Initial', cache=True)


@family_closure(family)
def CPU_fc(family):
    Bit = family.Bit
    BitVector = family.BitVector

    Idx = family.Idx
    Word = family.Word
    DWord = family.DWord

    isa = ISA_fc.Py
    RegisterFile = family.get_register_file()

    @family.assemble(locals(), globals())
    class CPU(Peak):
        def __init__(self):
            self.register_file = RegisterFile()

        @name_outputs(pc_next=isa.Word)
        def __call__(self,
                     inst: isa.Inst,
                     pc: isa.DWord) -> isa.DWord:


            op = inst.tag
            data = inst.data

            if data[isa.I16].match:
                i16 = data[isa.I16].value
                use_mask = Bit(1)
                use_imm = Bit(1)
                imm = i16.imm
                rd = i16.rd.idx
                rs1 = i16.rs1.idx
                rs2 = Idx(0)
            elif data[isa.R16].match:
                r16 = data[isa.R16].value
                use_imm = Bit(0)
                use_mask = Bit(1)
                imm = Word(0)
                rd = r16.rd.idx
                rs1 = r16.rs1.idx
                rs2 = r16.rs2.idx
            elif data[isa.I32].match:
                i32 = data[isa.I32].value
                use_mask = Bit(0)
                use_imm = Bit(1)
                imm = i32.imm
                rd = i32.rd.idx
                rs1 = i32.rs1.idx
                rs2 = Idx(0)
            else:
                assert data[isa.R32].match
                r32 = data[isa.R32].value
                use_mask = Bit(0)
                use_imm = Bit(0)
                imm = Word(0)
                rd = r32.rd.idx
                rs1 = r32.rs1.idx
                rs2 = r32.rs2.idx

            if use_mask:
                mask = ~(DWord(-1) << Word.size)
            else:
                mask = DWord(-1)

            a = self.register_file.load1(rs1) & mask

            if use_imm:
                b = imm.zext(DWord.size - Word.size)
            else:
                b = self.register_file.load2(rs2) & mask

            if op == isa.ADD or op == isa.SUB:
                if op == isa.SUB:
                    b = -b
                c = (a + b) & mask
            elif op == isa.AND:
                c = a & b
            else:
                assert op == isa.OR
                c = a | b

            self.register_file.store(rd, c)
            return pc + 4

    return CPU


@family_closure(family)
def CPU_mappable_fc(family):
    CPU = CPU_fc(family)
    Word = family.Word
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class CPU_mappable(Peak):
        def __init__(self):
            self.cpu = CPU()

        @name_outputs(pc_next=isa.Word, rd=isa.Word)
        def __call__(self,
                     inst: Const(isa.Inst),
                     pc: isa.DWord,
                     rs1_w: isa.Word,
                     rs2_w: isa.Word,
                     rs1_dw: isa.DWord,
                     rs2_dw: isa.DWord,
                     ) -> (isa.DWord, isa.DWord):

            if inst[isa.Inst16].match:
                rs1 = rs1_w.zext(DWord.size - Word.size)
                rs2 = rs2_w.zext(DWord.size - Word.size)
            else:
                rs1 = rs1_dw
                rs2 = rs2_dw

            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            pc_next = self.riscv(inst, pc)
            return pc_next, self.cpu.register_file.rd

        def _set_rs1_(self, rs1):
            self.cpu.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.cpu.register_file._set_rs2_(rs2)

    return CPU_mappable
