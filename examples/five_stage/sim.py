from types import SimpleNamespace

import hwtypes as ht
from peak import Peak, name_outputs, family_closure, Const

# from .isa import ISA_fc
# from .util import Initial
from . import family

WORDSIZE = 32

@family_closure(family)
def isa(family):
    Bit = family.Bit
    BitVector = family.BitVector

    AddrT = DataT = BitVector[WORDSIZE]
    InstT = BitVector[WORDSIZE]
    IdxT  = BitVector[5]

    class FetchOut(ht.Product):
        inst = InstT
        pc_inc = AddrT

    class ControlEx(ht.Product):
        ALUOp = BitVector[2]
        RegDst = Bit
        ALUSrc = Bit

    class ControlMem(ht.Product):
        MemRead = Bit
        MemWrite = Bit
        Branch = Bit

    class ControlWB(ht.Product):
        RegWrite = Bit
        MemtoReg = Bit

    class DecodeOut(ht.Product):
        read_data_1 = DataT
        read_data_2 = DataT
        extend_data = DataT
        write_idx_1 = IdxT
        write_idx_2 = IdxT

    class ExecOut(ht.Product):
        branch_target = AddrT
        zero = Bit
        alu_res = DataT
        reg_data = DataT
        write_idx = IdxT

    class MemOut(ht.Product):
        mem_data = DataT
        alu_res = DataT
        write_idx = IdxT

    return SimpleNamespace(**locals())

@family_closure(family)
def Top(family):
    isa_py = isa.Py

    FetchOut = isa_py.FetchOut
    ControlEx = isa_py.ControlEx
    ControlMem = isa_py.ControlMem
    ControlWB = isa_py.ControlWB
    DecodeOut = isa_py.DecodeOut
    ExecOut = isa_py.ExecOut
    MemOut = isa_py.MemOut

    Bit = family.Bit
    BitVector = family.BitVector

    FetchOutBuilder = family.get_constructor(FetchOut)

    AddrT = DataT = BitVector[WORDSIZE]
    InstT = BitVector[WORDSIZE]
    IdxT  = BitVector[5]

    
    CtrlT = BitVector[4]

    @family.compile(locals(), globals())
    class ALU(Peak):

        # MIPS encodings copied from final column in Fig. 4.47
        #   0000 => AND
        #   0001 =>  OR
        #   0010 => ADD
        #   0110 => SUB
        #   0111 => SLT (res=1 if (a < b) else res=0)

        def __call__(self, ctrl: CtrlT, i0: DataT, i1: DataT) -> (DataT, Bit):

            # Unused (always 0) for MIPS, see above
            if ctrl[3]:
                i0 = ~i0

            # ctrl[2] == 1 means want to do (i0 - i1)
            if ctrl[2]:
                i1 = ~i1

            # Need two's complement of i1 to do (i0 - i1)
            # i.e. will do (i0 + ~i1 + 1) if (ctrl[2] == 1)
            cin = ctrl[2]

            # Calculates (i0+i1) if (ctrl[2]==0) else (i0-i1)
            sum, cout = i0.adc(i1, cin)

            o = i0 | i1
            a = i0 & i1

            SIGNED=True
            if SIGNED:
                # Signed compare; sign bit of (a-b) tells whether a<b
                slt_int = sum[-1]
            else:
                # Unsigned compare; carry-out of (a-b) tells whether a<b
                slt_int = ~cout

            # Want slt = 32'b1 if i0<i1 else 32'b0
            slt = (BitVector[1](slt_int)).zext(WORDSIZE-1)

            if ctrl[1]:
                if ctrl[0]:
                    res = slt  # SLT (0x00000000 or 0x00000001)
                else:
                    res = sum  # SUM (ADD OR SUB)
            else:
                if ctrl[0]:
                    res = o    # OR
                else:
                    res = a    # AND

            z = (res == 0)
            return res, z


    @family.assemble(locals(), globals())
    class Fetch(Peak):
        def __init__(self):
            self.pc = family.gen_attr_register(DataT, 0)() # (init to zero)
            # self.imem = SRAM()

        def __call__(self, pc_calc: AddrT, pc_src: Bit) -> FetchOut:

            current_pc = self.pc

            # Build the adder
            incremented_pc = current_pc + 4

            # Build the mux
            if pc_src:
                self.pc = pc_calc
            else:
                self.pc = incremented_pc

            # Build the instruction memory
            # instruction = self.imem[current_pc]
            instruction = InstT(0)
            # Signals headed for the IF/ID (Fetch/Decode) boundary (register)
            return FetchOutBuilder(inst=instruction, pc_inc=incremented_pc)


    @family.assemble(locals(), globals())
    class Decode(Peak):
        def __call__(self, inst: InstT, reg_write: Bit, write_data: DataT, write_idx: IdxT) -> (
                DecodeOut, ControlEx, ControlMem, ControlWB):
            pass

    @family.assemble(locals(), globals())
    class Exec(Peak):
        def __call__(self,
                     # from control
                     ALUOp: BitVector[2],
                     ALUSrc: Bit,
                     RegDst: Bit,
                     # from data
                     pc_inc: AddrT,
                     read_data_1: DataT,
                     read_data_2: DataT,
                     extend_data: DataT,
                     write_idx_1: IdxT,
                     write_idx_2: IdxT,
                     ) -> ExecOut:
            pass


    @family.assemble(locals(), globals())
    class Mem(Peak):
        def __call__(self,
                     # from control
                     MemRead: Bit,
                     MemWrite: Bit,
                     Branch: Bit,
                     # from data
                     alu_res: AddrT,
                     reg_data: DataT,
                     ) -> MemOut:
            pass


    @family.assemble(locals(), globals())
    class Pipelined(Peak):
        def __init__(self):
            pass

    return ALU
