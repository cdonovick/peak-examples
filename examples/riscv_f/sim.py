from peak import Peak, name_outputs, family_closure, Const
from peak.float import float_lib_gen, RoundingMode 

from .isa import ISA_fc
from .util import Initial
from . import family

float_fcs = float_lib_gen(8, 23)

# Named R32I to make testing easier
@family_closure(family)
def R32I_fc(family):
    Bit = family.Bit
    BitVector = family.BitVector
    Unsigned = family.Unsigned
    Signed = family.Signed
    Word = family.Word
    Idx = family.Idx


    isa = ISA_fc.Py
    RegisterFile = family.get_register_file(2)
    FRegisterFile = family.get_register_file(3)

    ExecInst = family.get_constructor(isa.AluInst)
    FExecInst =  family.get_constructor(isa.FPUInst)
    DecodeOut = family.get_constructor(isa._DecodeOut)
    RM = family.get_constructor(isa.RM)

    RoundingMode_c = family.get_constructor(RoundingMode)
    @family.assemble(locals(), globals())
    class Decode(Peak):
        def __call__(self,
                inst: isa.Inst,
                pc: isa.Word,
                ) -> isa._DecodeOut:

            # Set up defaults
            use_imm = Bit(0)
            use_pc = Bit(0)
            mask_lsb = Bit(0)
            is_fp = Bit(0)
            is_branch = Bit(0)
            is_jump = Bit(0)
            cmp_zero = Bit(0)
            invert = Bit(0)

            # Note rd != 0 is implicit enable
            rd = Idx(0)
            rs1 = Idx(0)
            rs2 = Idx(0)
            rs3 = Idx(0)
            imm = Word(0)

            exec_inst = ExecInst(arith=isa.ArithInst.ADD)
            f_exec_inst = FExecInst(compute=isa.FPComputeInst.FADD)
            rm = RM(isa.RM.RNE)

            if inst[isa.OP].match:
                op_inst = inst[isa.OP].value
                rs1 = op_inst.data.rs1
                rs2 = op_inst.data.rs2
                exec_inst = op_inst.tag
                rd = op_inst.data.rd

            elif inst[isa.OP_IMM].match:
                op_imm_inst = inst[isa.OP_IMM].value
                if op_imm_inst.arith.match:
                    op_imm_arith_inst = op_imm_inst.arith.value
                    # Will need to manual add this to the constraints
                    # for mapping there is no SUBI because but can always
                    # do ADDI -imm.  However blocking in the ISA would
                    # radically increase its complexity.
                    assert op_imm_arith_inst.tag != isa.ArithInst.SUB

                    rs1 = op_imm_arith_inst.data.rs1
                    imm = op_imm_arith_inst.data.imm.sext(20)
                    use_imm = Bit(1)
                    exec_inst = ExecInst(arith=op_imm_arith_inst.tag)
                    rd = op_imm_arith_inst.data.rd

                else:
                    assert op_imm_inst.shift.match
                    op_imm_shift_inst = op_imm_inst.shift.value
                    rs1 = op_imm_shift_inst.data.rs1
                    imm = op_imm_shift_inst.data.imm.zext(27)
                    use_imm = Bit(1)
                    exec_inst = ExecInst(shift=op_imm_shift_inst.tag)
                    rd = op_imm_shift_inst.data.rd

            elif inst[isa.LUI].match:
                lui_inst = inst[isa.LUI].value.data
                imm = lui_inst.imm.sext(12) << 12
                rd = lui_inst.rd
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)

            elif inst[isa.AUIPC].match:
                auipc_inst = inst[isa.AUIPC].value.data
                use_pc = Bit(1)
                imm = auipc_inst.imm.sext(12) << 12
                rd = auipc_inst.rd
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)

            elif inst[isa.JAL].match:
                is_jump = Bit(1)
                jal_inst = inst[isa.JAL].value.data
                use_pc = Bit(1)
                imm = jal_inst.imm.sext(12) << 1
                rd = jal_inst.rd
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)

            elif inst[isa.JALR].match:
                is_jump = Bit(1)
                mask_lsb = Bit(1)
                jalr_inst = inst[isa.JALR].value.data
                rs1 = jalr_inst.rs1
                imm = jalr_inst.imm.sext(20)
                rd = jalr_inst.rd
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)

            elif inst[isa.Branch].match:
                is_branch = Bit(1)
                branch_inst = inst[isa.Branch].value
                rs1 = branch_inst.data.rs1
                rs2 = branch_inst.data.rs2
                imm = branch_inst.data.imm.sext(20) << 1

                # hand coded common sub-expr elimin
                is_eq = branch_inst.tag == isa.BranchInst.BEQ
                is_ne = branch_inst.tag == isa.BranchInst.BNE
                is_bge = branch_inst.tag == isa.BranchInst.BGE
                is_signed = is_bge | (branch_inst.tag == isa.BranchInst.BLT)
                cmp_ge = is_bge | (branch_inst.tag == isa.BranchInst.BGEU)

                if (is_eq | is_ne):
                    # for equality comparisons we use an xor
                    exec_inst = ExecInst(arith=isa.ArithInst.XOR)
                    # compare the output to 0
                    cmp_zero = Bit(1)
                    # invert the result for ne
                    invert = is_ne
                else:
                    # Reuse SLT and SLTU
                    if is_signed:
                        exec_inst = ExecInst(arith=isa.ArithInst.SLT)
                    else:
                        exec_inst = ExecInst(arith=isa.ArithInst.SLTU)
                    # invert if we are doing a greater than
                    invert = cmp_ge

            elif inst[isa.Load].match:
                # NOT IMPLEMENTED
                pass
            elif inst[isa.Store].match:
                # NOT IMPLEMENTED
                pass
            elif inst[isa.OP_FP].match:
                is_fp = Bit(1)
                op_fp_inst = inst[isa.OP_FP].value
                if op_fp_inst.compute.match:
                    rs1 = op_fp_inst.compute.value.data.rs1
                    rs2 = op_fp_inst.compute.value.data.rs2
                    rd = op_fp_inst.compute.value.data.rd
                    rm = op_fp_inst.compute.value.rm
                    f_exec_inst = FExecInst(compute=op_fp_inst.compute.value.tag)
                elif op_fp_inst.minmax.match:
                    rs1 = op_fp_inst.minmax.value.data.rs1
                    rs2 = op_fp_inst.minmax.value.data.rs2
                    rd = op_fp_inst.minmax.value.data.rd
                    f_exec_inst = FExecInst(minmax=op_fp_inst.minmax.value.tag)
                elif op_fp_inst.sqrt.match:
                    rs1 = op_fp_inst.sqrt.value.data.rs1
                    rd = op_fp_inst.sqrt.value.data.rd
                    rm = op_fp_inst.sqrt.value.rm
                    f_exec_inst = FExecInst(other=isa.FPOther.FSQRT)
                elif op_fp_inst.compare.match:
                    rs1 = op_fp_inst.compare.value.data.rs1
                    rs2 = op_fp_inst.compare.value.data.rs2
                    rd = op_fp_inst.compare.value.data.rd
                    f_exec_inst = FExecInst(compare=op_fp_inst.compare.value.tag)
                else:
                    assert op_fp_inst.class_.match
                    f_exec_inst = FExecInst(other=isa.FPOther.FCLASS)
                    # Not implemented
            else:
                assert inst[isa.OP_FUSED].match
                is_fp = Bit(1)
                op_fused_inst = inst[isa.OP_FUSED].value
                rs1 = op_fused_inst.data.rs1
                rs2 = op_fused_inst.data.rs2
                rs3 = op_fused_inst.data.rs3
                rd = op_fused_inst.data.rd
                rm = op_fused_inst.rm
                f_exec_inst = FExecInst(fused=op_fused_inst.tag)

            return DecodeOut(
                rs1 = rs1,
                rs2 = rs2,
                rs3 = rs3,
                rd = rd,
                imm = imm,
                use_imm = use_imm,
                use_pc = use_pc,
                exec_inst = exec_inst,
                f_exec_inst = f_exec_inst,
                rm = rm,
                mask_lsb = mask_lsb,
                is_fp = is_fp,
                is_branch = is_branch,
                is_jump = is_jump,
                cmp_zero = cmp_zero,
                invert = invert,
            )


    @family.assemble(locals(), globals())
    class ALU(Peak):
        def __call__(self,
                exec_inst: isa.AluInst,
                a: isa.Word,
                b: isa.Word,
            ) -> isa.Word:
            if exec_inst.arith.match:
                arith_inst = exec_inst.arith.value
                if arith_inst == isa.ArithInst.ADD:
                    c = a + b
                elif arith_inst == isa.ArithInst.SUB:
                    c = a - b
                elif arith_inst == isa.ArithInst.SLT:
                    c = Word(a.bvslt(b))
                elif arith_inst == isa.ArithInst.SLTU:
                    c = Word(a.bvult(b))
                elif arith_inst == isa.ArithInst.AND:
                    c = a & b
                elif arith_inst == isa.ArithInst.OR:
                    c = a | b
                else:
                    assert arith_inst == isa.ArithInst.XOR
                    c = a ^ b
            else:
                assert exec_inst.shift.match
                shift_inst = exec_inst.shift.value
                if shift_inst == isa.ShiftInst.SLL:
                    c = a.bvshl(b)
                elif shift_inst == isa.ShiftInst.SRL:
                    c = a.bvlshr(b)
                else:
                    assert shift_inst == isa.ShiftInst.SRA
                    c = a.bvashr(b)
            return c

    @family.assemble(locals(), globals())
    class FPU(Peak):
        def __init__(self):
            self.fp_add = float_fcs.Add_fc(family)()
            self.fp_sub = float_fcs.Sub_fc(family)()
            self.fp_mul = float_fcs.Mul_fc(family)()
            self.fp_div = float_fcs.Div_fc(family)()
            self.fp_sqrt = float_fcs.Sqrt_fc(family)()
            self.fp_min = float_fcs.Min_fc(family)()
            self.fp_max = float_fcs.Max_fc(family)()
            self.fp_fma = float_fcs.Fma_fc(family)()
            self.fp_neg_1 = float_fcs.Neg_fc(family)()
            self.fp_neg_2 = float_fcs.Neg_fc(family)()
            self.fp_eq = float_fcs.Eq_fc(family)()
            self.fp_leq = float_fcs.Leq_fc(family)()
            self.fp_lt = float_fcs.Lt_fc(family)()


        def __call__(self,
                inst: isa.FPUInst,
                rm: isa.RM,
                a: isa.Word,
                b: isa.Word,
                c: isa.Word,
                ) -> isa.Word:
            add_in_0 = Word(0)
            add_in_1 = Word(0)
            sub_in_0 = Word(0)
            sub_in_1 = Word(0)
            mul_in_0 = Word(0)
            mul_in_1 = Word(0)
            div_in_0 = Word(0)
            div_in_1 = Word(0)
            min_in_0 = Word(0)
            min_in_1 = Word(0)
            max_in_0 = Word(0)
            max_in_1 = Word(0)
            fma_in_0 = Word(0)
            fma_in_1 = Word(0)
            fma_in_2 = Word(0)
            eq_in_0 = Word(0)
            eq_in_1 = Word(0)
            lt_in_0 = Word(0)
            lt_in_1 = Word(0)
            le_in_0 = Word(0)
            le_in_1 = Word(0)
            sqrt_in = Word(0)

            #HACK
            rm = RoundingMode_c(RoundingMode.RNE)

            if inst.compute.match:
                if inst.compute.value == isa.FPComputeInst.FADD:
                    add_in_0 = a
                    add_in_1 = b
                elif inst.compute.value == isa.FPComputeInst.FSUB:
                    sub_in_0 = a
                    sub_in_1 = b
                elif inst.compute.value == isa.FPComputeInst.FMUL:
                    mul_in_0 = a
                    mul_in_1 = b
                else:
                    assert inst.compute.value == isa.FPComputeInst.FDIV
                    div_in_0 = a
                    div_in_1 = b
            elif inst.minmax.match:
                if inst.minmax.value == isa.FPMinMaxInst.MIN:
                    min_in_0 = a
                    min_in_1 = b
                else:
                    assert inst.minmax.value == isa.FPMinMaxInst.MAX
                    max_in_0 = a
                    max_in_1 = b
            elif inst.compare.match:
                if inst.compare.value == isa.FPCompareInst.EQ:
                    eq_in_0 = a
                    eq_in_1 = b
                elif inst.compare.value == isa.FPCompareInst.LT:
                    lt_in_0 = a
                    lt_in_1 = b
                else:
                    assert inst.compare.value == isa.FPCompareInst.LE
                    le_in_0 = a
                    le_in_1 = b
            elif inst.fused.match:
                fma_in_0 = a
                fma_in_1 = b
                fma_in_2 = c
                if (inst.fused.value == isa.FPFusedInst.FNMA) or (inst.fused.value == isa.FPFusedInst.FNMS):
                    fma_in_0 = self.fp_neg_1(rm, fma_in_0)

                if (inst.fused.value == isa.FPFusedInst.FMS) or (inst.fused.value == isa.FPFusedInst.FNMS):
                    fma_in_2 = self.fp_neg_2(rm, fma_in_2)
            else:
                assert inst.other.match
                if inst.other.value == isa.FPOther.FSQRT:
                    sqrt_in = a
                else:
                    assert inst.other.value == isa.FPOther.FCLASS
                    # Not Implemented



            add_out = self.fp_add(rm, add_in_0, add_in_1)
            sub_out = self.fp_sub(rm, sub_in_0, sub_in_1)
            mul_out = self.fp_mul(rm, mul_in_0, mul_in_1)
            div_out = self.fp_div(rm, div_in_0, div_in_1)
            min_out = self.fp_min(rm, min_in_0, min_in_1)
            max_out = self.fp_max(rm, max_in_0, max_in_1)
            eq_out = Word(self.fp_eq(rm, eq_in_0, eq_in_1))
            lt_out = Word(self.fp_lt(rm, lt_in_0, lt_in_1))
            le_out = Word(self.fp_leq(rm, le_in_0, le_in_1))
            fma_out = self.fp_fma(rm, fma_in_0, fma_in_1, fma_in_2)
            sqrt_out = self.fp_sqrt(rm, sqrt_in)

            if inst.compute.match:
                if inst.compute.value == isa.FPComputeInst.FADD:
                    return add_out
                elif inst.compute.value == isa.FPComputeInst.FSUB:
                    return sub_out
                elif inst.compute.value == isa.FPComputeInst.FMUL:
                    return mul_out
                else:
                    return div_out
            elif inst.minmax.match:
                if inst.minmax.value == isa.FPMinMaxInst.MIN:
                    return min_out
                else:
                    return max_out
            elif inst.compare.match:
                if inst.compare.value == isa.FPCompareInst.EQ:
                    return eq_out
                elif inst.compare.value == isa.FPCompareInst.LT:
                    return lt_out
                else:
                    return le_out
            elif inst.fused.match:
                return fma_out
            else:
                if inst.other.value == isa.FPOther.FSQRT:
                    return sqrt_out
                else:
                    return Word(0)


    @family.assemble(locals(), globals())
    class R32I(Peak):
        def __init__(self):
            self.register_file = RegisterFile()
            self.f_register_file = FRegisterFile()
            self.Decode = Decode()
            self.ALU = ALU()
            self.FPU = FPU()

        @name_outputs(pc_next=isa.Word)
        def __call__(self,
                     inst: isa.Inst,
                     pc: isa.Word) -> isa.Word:
            # Decode
            decoded = self.Decode(inst, pc)

            # unpack
            rs1 = decoded.rs1
            rs2 = decoded.rs2
            rs3 = decoded.rs3
            rd = decoded.rd
            imm = decoded.imm
            use_imm = decoded.use_imm
            use_pc = decoded.use_pc
            exec_inst = decoded.exec_inst
            f_exec_inst = decoded.f_exec_inst
            rm = decoded.rm
            mask_lsb = decoded.mask_lsb
            is_fp = decoded.is_fp
            is_branch = decoded.is_branch
            is_jump = decoded.is_jump
            cmp_zero = decoded.cmp_zero
            invert = decoded.invert

            a = self.register_file.load1(rs1)
            b = self.register_file.load2(rs2)

            fa = self.f_register_file.load1(rs1)
            fb = self.f_register_file.load2(rs2)
            fc = self.f_register_file.load3(rs3)

            if use_pc:
                a = pc

            if use_imm:
                b = imm

            # Execute
            c = self.ALU(exec_inst, a, b)
            fpu_out = self.FPU(f_exec_inst, rm, fa, fb, fc)

            if mask_lsb:
                c = BitVector[1](0).concat(c[1:]) # clear bottom bit for jalr

            # Commit
            assert not (is_jump & is_branch)

            pc_next = pc + 4
            branch_target = pc + imm
            if is_branch:
                out = Word(0)
                if cmp_zero:
                    cond = (c == 0)
                else:
                    cond = c[0]

                cond = cond ^ invert
                if cond:
                    pc_next = branch_target

            elif is_jump:
                out = pc_next
                pc_next = c
            elif is_fp:
                out = fpu_out
            else:
                out = c

            self.register_file.store(rd, out)
            return pc_next
    return R32I


@family_closure(family)
def R32I_mappable_fc(family):
    R32I = R32I_fc(family)
    Word = family.Word
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class R32I_mappable(Peak):
        def __init__(self):
            self.riscv = R32I()

        @name_outputs(pc_next=isa.Word, rd=isa.Word, f_rd=isa.Word)
        def __call__(self,
                     inst: Const(isa.Inst),
                     pc: isa.Word,
                     rs1: isa.Word,
                     rs2: isa.Word,
                     rd: Initial(isa.Word),
                     f_rs1: isa.Word,
                     f_rs2: isa.Word,
                     f_rs3: isa.Word,
                     f_rd: Initial(isa.Word)
                     ) -> (isa.Word, isa.Word, isa.Word):

            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            self._set_rd_(rd)
            self._set_f_rs1_(f_rs1)
            self._set_f_rs2_(f_rs2)
            self._set_f_rs3_(f_rs3)
            self._set_f_rd_(f_rd)
            pc_next = self.riscv(inst, pc)
            return pc_next, self.riscv.register_file.rd, self.riscv.f_register_file.rd

        def _set_rs1_(self, rs1):
            self.riscv.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.riscv.register_file._set_rs2_(rs2)

        def _set_rd_(self, rd):
            self.riscv.register_file._set_rd_(rd)

        def _set_f_rs1_(self, rs1):
            self.riscv.f_register_file._set_rs1_(rs1)

        def _set_f_rs2_(self, rs2):
            self.riscv.f_register_file._set_rs2_(rs2)

        def _set_f_rs3_(self, rs3):
            self.riscv.f_register_file._set_rs3_(rs3)

        def _set_f_rd_(self, rd):
            self.riscv.f_register_file._set_rd_(rd)

    return R32I_mappable

