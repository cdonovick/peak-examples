import functools as ft

from peak import Peak, name_outputs, family_closure, Const


from .isa import ISA_fc
from .util import Initial, clo
from . import family
from .micro import Micro_fc



@family_closure(family)
def MIPS32_fc(family):
    Bit = family.Bit
    BitVector = family.BitVector
    Unsigned = family.Unsigned
    Signed = family.Signed
    Word = family.Word
    Idx = family.Idx


    isa = ISA_fc.Py
    RegisterFile = family.get_register_file()

    micro = Micro_fc.Py

    ALUControl = family.get_constructor(micro.ALUControl)
    ALUOp = family.get_constructor(micro.ALUOp)

    def _enum_in(e, vals):
        return ft.reduce(lambda c, x: c | (e == x), vals, Bit(0))

    @family.assemble(locals(), globals())
    class MIPS32(Peak):
        def __init__(self):
            self.register_file = RegisterFile()
            self.alu = ALU()

        @name_outputs(acc=isa.BitVector[64])
        def __call__(self,
                     inst: isa.Inst,
                     acc: isa.BitVector[64],
                     ) -> isa.BitVector[64]:
            write_hi = Bit(0)
            write_lo = Bit(0)
            add_acc = Bit(0)
            sub_acc = Bit(0)
            rd = Idx(0)
            rs = Idx(0)
            rt = Idx(0)
            a = Word(0)
            b = Word(0)
            cl = Word(0)
            ch = Word(0)
            signed = Bit(0)
            # 5 bit shift amount
            s5 = BitVector[5](0)
            t5 = BitVector[5](0)
            # 16 bit imm
            i16 = BitVector[16](0)

            is_mov = Bit(0)

            alu_ctrl = ALUControl(
                    signed=Bit(0),
                    alu_op=micro.ALUOp.OR,
                    inv_lu_out=Bit(0),
            )

            if inst[isa.R1].match:
                if inst[isa.R1].value.op.dir == isa.TF.T:
                    _write = Bit(1)
                    rs = inst[isa.R1].value.rd
                else:
                    _write = Bit(0)
                    rd = inst[isa.R1].value.rd

                _read   = ~_write
                _use_lo = inst[isa.R1].value.op.reg == isa.LOHI.LO
                _use_hi = ~_use_lo

                if _read & _use_hi:
                    a = a | acc[32:]
                elif _read & _use_lo:
                    a = a | acc[:32]

                write_hi = _write & _use_hi
                write_lo = _write & _use_lo

            elif inst[isa.R2].match:
                rd = inst[isa.R2].value.rd
                rs = inst[isa.R2].value.rs
                _r2_op = inst[isa.R2].value.op
                signed = _enum_in(_r2_op, (isa.R2Inst.DIV, isa.R2Inst.MADD, isa.R2Inst.MSUB, isa.R2Inst.MULT))
                _unsigned = _enum_in(_r2_op, (isa.R2Inst.DIVU, isa.R2Inst.MADDU, isa.R2Inst.MSUBU, isa.R2Inst.MULTU))
                inv_lu_out = _r2_op == isa.R2Inst.CLZ

                if _enum_in(_r2_op, (isa.R2Inst.DIV, isa.R2Inst.DIVU)):
                    rt = rs
                    rs = rd
                    rd = Idx(0)
                    write_hi = Bit(1)
                    write_lo = Bit(1)
                    alu_op = ALUOp(micro.ALUOp.DIV)
                elif _enum_in(_r2_op, (isa.R2Inst.MULT, isa.R2Inst.MULTU)):
                    rt = rs
                    rs = rd
                    rd = Idx(0)
                    write_hi = Bit(1)
                    write_lo = Bit(1)
                    alu_op = ALUOp(micro.ALUOp.MUL)
                elif _enum_in(_r2_op, (isa.R2Inst.CLO, isa.R2Inst.CLZ)):
                    alu_op = ALUOp(micro.ALUOp.CLO)
                else:
                    # Need to handle SEB, SEH, WSBH
                    alu_op  = ALUOp(micro.ALUOp.OR)
                    rd = Idx(0)
                    rs = Idx(0)
                alu_ctrl = ALUControl(signed=Bit(signed), alu_op=alu_op, inv_lu_out=Bit(inv_lu_out))
            elif inst[isa.R3].match:
                rd = inst[isa.R3].value.rd
                rs = inst[isa.R3].value.rs
                rt = inst[isa.R3].value.rt
                _r3_op = inst[isa.R3].value.op
                signed = _enum_in(_r3_op, (isa.R3Inst.SLT, isa.R3Inst.SRAV, isa.R3Inst.MUL))
                inv_lu_out = _enum_in(_r3_op, (isa.R3Inst.SUBU, isa.R3Inst.NOR, isa.R3Inst.MOVN))
                if _enum_in(_r3_op, (isa.R3Inst.SUBU, isa.R3Inst.ADDU)):
                    alu_op = ALUOp(micro.ALUOp.ADD)
                elif _enum_in(_r3_op, (isa.R3Inst.OR, isa.R3Inst.NOR)):
                    alu_op = ALUOp(micro.ALUOp.OR)
                elif _enum_in(_r3_op, (isa.R3Inst.SLT, isa.R3Inst.SLTU)):
                    alu_op = ALUOp(micro.ALUOp.LT)
                elif _r3_op == isa.R3Inst.AND:
                    alu_op = ALUOp(micro.ALUOp.AND)
                elif _r3_op == isa.R3Inst.XOR:
                    alu_op = ALUOp(micro.ALUOp.XOR)
                elif _enum_in(_r3_op, (isa.R3Inst.SRLV, isa.R3Inst.SRAV)):
                    alu_op = ALUOp(micro.ALUOp.SHR)
                elif _r3_op == isa.R3Inst.SLLV:
                    alu_op = ALUOp(micro.ALUOp.SHL)
                elif _r3_op == isa.R3Inst.ROTRV:
                    alu_op = ALUOp(micro.ALUOp.ROT)
                elif _r3_op == isa.R3Inst.MUL:
                    alu_op = ALUOp(micro.ALUOp.MUL)
                else:
                    alu_op = ALUOp(micro.ALUOp.MOV)
                    is_mov = Bit(1)
                alu_ctrl = ALUControl(signed=Bit(signed), alu_op=alu_op, inv_lu_out=Bit(inv_lu_out))
            elif inst[isa.Rs].match:
                rd = inst[isa.Rs].value.rd
                rs = inst[isa.Rs].value.rs
                b = inst[isa.Rs].value.sa.zext(27)
                signed = inst[isa.Rs].value.op == isa.RsInst.SRA
                if signed or (inst[isa.Rs].value.op == isa.RsInst.SRL):
                    alu_op = ALUOp(micro.ALUOp.SHR)
                elif inst[isa.Rs].value.op == isa.RsInst.SLL:
                    alu_op = ALUOp(micro.ALUOp.SHL)
                else:
                    alu_op = ALUOp(micro.ALUOp.ROT)
                alu_ctrl = ALUControl(signed=Bit(signed), alu_op=alu_op, inv_lu_out=Bit(0))
            elif inst[isa.Rlm].match:
                rd = inst[isa.Rlm].value.rd
                rs = inst[isa.Rlm].value.rs
                s5 = inst[isa.Rlm].value.mb
                t5 = inst[isa.Rlm].value.lb
                # Need to handle EXT / INS
                rd = Idx(0)
                rs = Idx(0)
            elif inst[isa.I2].match:
                rd = inst[isa.I2].value.rd
                rs = inst[isa.I2].value.rs
                i16 = inst[isa.I2].value.im
                signed = inst[isa.I2].value.op == isa.I2Inst.SLTI
                if inst[isa.I2].value.op == isa.I2Inst.ADDIU:
                    alu_op = ALUOp(micro.ALUOp.ADD)
                elif inst[isa.I2].value.op == isa.I2Inst.ANDI:
                    alu_op = ALUOp(micro.ALUOp.AND)
                elif inst[isa.I2].value.op == isa.I2Inst.ORI:
                    alu_op = ALUOp(micro.ALUOp.OR)
                elif inst[isa.I2].value.op == isa.I2Inst.XORI:
                    alu_op = ALUOp(micro.ALUOp.XOR)
                else:
                    alu_op = ALUOp(micro.ALUOp.LT)
                alu_ctrl = ALUControl(signed=Bit(signed), alu_op=alu_op, inv_lu_out=Bit(0))

            else:
                assert inst[isa.LUI].match
                rd = inst[isa.LUI].value.rd
                b = BitVector[16](0).concat(inst[isa.LUI].value.im)
                alu_ctrl = ALUControl(signed=Bit(0), alu_op=ALUOp(micro.ALUOp.ADD), inv_lu_out=Bit(0))

            a_ = self.register_file.load1(rs)
            b_ = self.register_file.load2(rt)
            a = a | a_
            b = b | b_
            if signed:
                i32 = i16.sext(16)
            else:
                i32 = i16.zext(16)

            b = b | i32

            cl, ch = self.alu(alu_ctrl, a, b)
            if is_mov and cl[0]:
                cl = a
            elif is_mov:
                rd = Idx(0)

            if write_lo & write_hi:
                acc_out = cl.concat(ch)
            elif write_lo:
                acc_out = cl.concat(acc[:32])
            elif write_hi:
                acc_out = acc[32:].concat(ch)
            elif add_acc:
                acc_out = acc + cl.concat(ch)
            elif sub_acc:
                acc_out = acc - cl.concat(ch)
            else:
                acc_out = acc

            self.register_file.store(rd, cl)

            return acc_out


    @family.assemble(locals(), globals())
    class ALU(Peak):
        @name_outputs(
                cl=Word,
                ch=Word,
                )
        def __call__(self,
                inst: micro.ALUControl,
                a: Word,
                b: Word,
                ) -> (Word, Word):
            if inst.alu_op == micro.ALUOp.AND:
                lu_out = a & b
            elif inst.alu_op == micro.ALUOp.OR:
                lu_out = a | b
            elif inst.alu_op == micro.ALUOp.XOR:
                lu_out = a ^ b
            elif inst.alu_op == micro.ALUOp.MOV:
                lu_out = b.bvcomp(0).sext(31)
            elif inst.alu_op == micro.ALUOp.CLO:
                lu_out = a
            else:
                lu_out = b

            if inst.inv_lu_out:
                lu_out = ~lu_out
                if inst.alu_op == micro.ALUOp.ADD:
                    lu_out = lu_out + 1

            if inst.signed:
                _a = a.sext(32)
                _b = b.sext(32)
            else:
                _a = a.zext(32)
                _b = b.zext(32)

            sa = b[:5].zext(27)
            ch = Word(0)
            if inst.alu_op == micro.ALUOp.ADD:
                cl = a + lu_out
            elif inst.alu_op == micro.ALUOp.MUL:
                _c = _a * _b
                cl = _c[:32]
                ch = _c[32:]
            elif inst.alu_op == micro.ALUOp.DIV:
                if inst.signed:
                    cl = a.bvsdiv(b)
                    ch = a.bvsrem(b)
                else:
                    cl = a.bvudiv(b)
                    ch = a.bvurem(b)
            elif inst.alu_op == micro.ALUOp.LT:
                if inst.signed:
                    cl = a.bvslt(b).ite(Word(1), Word(0))
                else:
                    cl = a.bvult(b).ite(Word(1), Word(0))
            elif inst.alu_op == micro.ALUOp.SHL:
                cl = a << sa
            elif inst.alu_op == micro.ALUOp.SHR:
                if inst.signed:
                    cl = a.bvashr(sa)
                else:
                    cl = a.bvlshr(sa)
            elif inst.alu_op == micro.ALUOp.ROT:
                _sb =  Word(32) - sa
                cl = a.bvlshr(sa) | a.bvshl(_sb)
            elif inst.alu_op == micro.ALUOp.CLO:
                cl = clo(lu_out)
            else:
                cl = lu_out

            return cl, ch
    return MIPS32


@family_closure(family)
def MIPS32_mappable_fc(family):
    MIPS32 = MIPS32_fc(family)
    Word = family.Word
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class MIPS32_mappable(Peak):
        def __init__(self):
            self.riscv = MIPS32()

        @name_outputs(rd=isa.Word, acc_out=isa.BitVector[64])
        def __call__(self,
                     inst: Const(isa.Inst),
                     rs1: isa.Word,
                     rs2: isa.Word,
                     rd: Initial(isa.Word),
                     acc: Initial(isa.BitVector[64]),
                     ) -> (isa.Word, isa.BitVector[64]):

            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            self._set_rd_(rd)
            acc_out = self.riscv(inst, acc)
            return self.riscv.register_file.rd, acc_out

        def _set_rs1_(self, rs1):
            self.riscv.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.riscv.register_file._set_rs2_(rs2)

        def _set_rd_(self, rd):
            self.riscv.register_file._set_rd_(rd)

    return MIPS32_mappable


@family_closure(family)
def MIPS32_mappable_no_rd_fc(family):
    MIPS32 = MIPS32_fc(family)
    Word = family.Word
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class MIPS32_mappable(Peak):
        def __init__(self):
            self.riscv = MIPS32()

        @name_outputs(rd=isa.Word, acc_out=isa.BitVector[64])
        def __call__(self,
                     inst: Const(isa.Inst),
                     rs1: isa.Word,
                     rs2: isa.Word,
                     acc: Initial(isa.BitVector[64]),
                     ) -> (isa.Word, isa.BitVector[64]):

            rd = Word(0x5555)
            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            self._set_rd_(rd)
            acc_out = self.riscv(inst, acc)
            return self.riscv.register_file.rd, acc_out

        def _set_rs1_(self, rs1):
            self.riscv.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.riscv.register_file._set_rs2_(rs2)

        def _set_rd_(self, rd):
            self.riscv.register_file._set_rd_(rd)

    return MIPS32_mappable
