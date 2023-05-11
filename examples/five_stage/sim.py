from types import SimpleNamespace

import hwtypes as ht
from peak import Peak, name_outputs, family_closure, Const

# from .isa import ISA_fc
# from .util import Initial
from . import family


@family_closure(family)
def isa(family):
    Bit = family.Bit
    BitVector = family.BitVector

    AddrT = DataT = BitVector[32]
    InstT = BitVector[32]
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

    AddrT = DataT = BitVector[32]
    InstT = BitVector[32]
    IdxT  = BitVector[5]

    
    CtrlT = BitVector[5]

    @family.compile(locals(), globals())
    class ALU(Peak):
        def __call__(self, ctrl: CtrlT, i0: DataT, i1: DataT) -> (DataT, Bit, Bit):
            if ctrl[3]:
                i0 = ~i0

            if ctrl[2]:
                i1 = ~i1

            cin = ctrl[2]
            s, cout = i0.adc(i1, cin)
            sovf = (i0[-1] == i1[-1]) & (s[-1] != i0[-1])

            o = i0 | i1
            a = i0 & i1

            if ctrl[4]:
                ovf = sovf
                set = s[-1:]
            else:
                ovf = cout
                set = BV[1](~cout)


            slt = set.zext(WORD_SIZE-1)

            if ctrl[1]:
                if ctrl[0]:
                    res = slt
                else:
                    res = s
            else:
                if ctrl[0]:
                    res = o
                else:
                    res = a

            z = res == 0
            return res, ovf, z


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

    # return Exec
    return Fetch
