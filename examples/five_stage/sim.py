import hwtypes as ht
from peak import Peak, name_outputs, family_closure, Const


from .isa import ISA_fc
from .util import Initial
from . import family


@family_closure(family)
def isa(family)
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

@family_closure(family)
def Top(family):
    Bit = family.Bit
    BitVector = family.BitVector

    AddrT = DataT = BitVector[32]
    InstT = BitVector[32]
    IdxT  = BitVector[5]


    @family.assemble(locals(), globals())
    class Fetch(Peak):
        def __call__(self, pc_calc: AddrT, pc_src: Bit) -> FetchOut:
            pass

    @family.assemble(locals(), globals())
    class Decode(Peak):
        def __call__(self, inst: InstT, reg_write: Bit, write_data: DataT, write_idx: IdxT) -> (DecodeOut, ControlEx, ControlMem, ControlWB):
            pass

    @family.assemble(locals(), globals())
    class Exec(Peak):
        def __call__(self,
                     # from control
                     ALUOp: BitVector[2],
                     ALUSrc: Bit,
                     RegDst: Bit,
                     # from data
                     pc_inc: AddrT
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
                     ):
            pass


    @family.assemble(locals(), globals())
    class Pipelined(Peak):
        def __init__(self):
            pass

    return Exec
