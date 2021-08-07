from peak import Peak, name_outputs, family_closure, Const


from .isa import ISA_fc
from .util import Initial
from . import family

@family_closure(family)
def R32I_fc(family):
    Bit = family.Bit
    BitVector = family.BitVector
    Unsigned = family.Unsigned
    Signed = family.Signed
    Word = family.Word
    Idx = family.Idx


    isa = ISA_fc.Py
    RegisterFile = family.get_register_file()
    ExecInst = family.get_constructor(isa.AluInst)
    DecodeOut = family.get_constructor(isa._DecodeOut)

    @family.assemble(locals(), globals())
    class Decode(Peak):
        def __call__(self,
                inst: isa.Inst,
                pc: isa.Word,
                ) -> isa._DecodeOut:

            use_imm = Bit(0)
            use_pc = Bit(0)
            mask_lsb = Bit(0)
            is_branch = Bit(0)
            is_jump = Bit(0)
            cmp_zero = Bit(0)
            invert = Bit(0)

            # Note rd != 0 is implicit enable
            rd = Idx(0)
            rs1 = Idx(0)
            rs2 = Idx(0)
            imm = Word(0)

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
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)
            else:
                assert inst[isa.Store].match
                exec_inst = ExecInst(arith=isa.ArithInst.ADD)
            return DecodeOut(
                rs1 = rs1,
                rs2 = rs2,
                rd = rd,
                imm = imm,
                use_imm = use_imm,
                use_pc = use_pc,
                exec_inst = exec_inst,
                mask_lsb = mask_lsb,
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
    class R32I(Peak):
        def __init__(self):
            self.register_file = RegisterFile()
            self.Decode = Decode()
            self.ALU = ALU()

        @name_outputs(pc_next=isa.Word)
        def __call__(self,
                     inst: isa.Inst,
                     pc: isa.Word) -> isa.Word:
            # Decode
            decoded = self.Decode(inst, pc)

            # unpack
            rs1 = decoded.rs1
            rs2 = decoded.rs2
            rd = decoded.rd
            imm = decoded.imm
            use_imm = decoded.use_imm
            use_pc = decoded.use_pc
            exec_inst = decoded.exec_inst
            mask_lsb = decoded.mask_lsb
            is_branch = decoded.is_branch
            is_jump = decoded.is_jump
            cmp_zero = decoded.cmp_zero
            invert = decoded.invert

            a = self.register_file.load1(rs1)
            b = self.register_file.load2(rs2)

            if use_pc:
                a = pc

            if use_imm:
                b = imm


            # Execute
            c = self.ALU(exec_inst, a, b)

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

        @name_outputs(pc_next=isa.Word, rd=isa.Word)
        def __call__(self,
                     inst: Const(isa.Inst),
                     pc: isa.Word,
                     rs1: isa.Word,
                     rs2: isa.Word,
                     rd: Initial(isa.Word),
                     ) -> (isa.Word, isa.Word):

            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            self._set_rd_(rd)
            pc_next = self.riscv(inst, pc)
            return pc_next, self.riscv.register_file.rd

        def _set_rs1_(self, rs1):
            self.riscv.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.riscv.register_file._set_rs2_(rs2)

        def _set_rd_(self, rd):
            self.riscv.register_file._set_rd_(rd)

    return R32I_mappable


@family_closure(family)
def R32I_mappable_no_pc_fc(family):
    R32I = R32I_fc(family)
    Word = family.Word
    isa = ISA_fc.Py


    @family.assemble(locals(), globals())
    class R32I_mappable(Peak):
        def __init__(self):
            self.riscv = R32I()

        @name_outputs(rd=isa.Word)
        def __call__(self,
                     inst: Const(isa.Inst),
                     rs1: isa.Word,
                     rs2: isa.Word,
                     ) -> isa.Word:

            pc = Word(0)
            rd = Word(0x5555)
            self._set_rs1_(rs1)
            self._set_rs2_(rs2)
            self._set_rd_(rd)
            pc_next = self.riscv(inst, pc)
            return self.riscv.register_file.rd

        def _set_rs1_(self, rs1):
            self.riscv.register_file._set_rs1_(rs1)

        def _set_rs2_(self, rs2):
            self.riscv.register_file._set_rs2_(rs2)

        def _set_rd_(self, rd):
            self.riscv.register_file._set_rd_(rd)

    return R32I_mappable
