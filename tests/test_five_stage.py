from examples.five_stage.sim import Top, isa

import pytest

def test_ALU():
    global isa

    isa_py = isa.Py
    ALU = Top.Py
    alu = ALU()

    # ADD
    ctrl = isa_py.BitVector[4](0b0010)
    i0 = isa_py.DataT(2)
    i1 = isa_py.DataT(2)

    res, z = alu(ctrl, i0, i1)

    assert (res == isa_py.DataT(4)), "BAD ADD"
    assert (z == 0), "oh no zero test failed"

    # SUB
    ctrl = isa_py.BitVector[4](0b0110)
    i0 = isa_py.DataT(2)
    i1 = isa_py.DataT(2)

    res, z = alu(ctrl, i0, i1)

    assert (res == isa_py.DataT(0)), "BAD SUB"
    assert (z != 0), "oh no zero test failed"

    SLT = isa_py.BitVector[4](0b0111)

    # SLT 2,1 should be 0
    (i0,i1) = (2,1)
    res, z = alu(SLT, isa_py.DataT(i0), isa_py.DataT(i1))
    want_res = 1 if (i0 < i1)        else 0
    want_z   = 1 if (want_res == 0)  else 0
    assert (res == isa_py.DataT(want_res)), "BAD SLT"
    assert (z == want_z), "oh no zero test failed"

    # SLT 1,2 should be 1 because 1<2
    (i0,i1) = (1,2) 
    res, z = alu(SLT, isa_py.DataT(i0), isa_py.DataT(i1))
    want_res = 1 if (i0 < i1)        else 0
    want_z   = 1 if (want_res == 0)  else 0
    assert (res == isa_py.DataT(want_res)), "BAD SLT"
    assert (z == want_z), "oh no zero test failed"

    # SLT 0,-1 should be 1
    (i0,i1) = (0,-1)
    res, z = alu(SLT, isa_py.DataT(i0), isa_py.DataT(i1))
    want_res = 1 if (i0 < i1)        else 0
    want_z   = 1 if (want_res == 0)  else 0
    assert (res == isa_py.DataT(want_res)), "BAD SLT"
    assert (z == want_z), "oh no zero test failed"

    # SLT 8,8
    (i0,i1) = (8,8)
    res, z = alu(SLT, isa_py.DataT(i0), isa_py.DataT(i1))
    want_res = 1 if (i0 < i1)        else 0
    want_z   = 1 if (want_res == 0)  else 0
    assert (res == isa_py.DataT(want_res)), "BAD SLT"
    assert (z == want_z), "oh no zero test failed"





@pytest.mark.skip
def test_five_stage():
    global isa
    isa_py = isa.Py

    Fetch = Top.Py

    fetch = Fetch()

#     def __call__(self,
#                  # from control
#                  ALUOp: BitVector[2],
#                  ALUSrc: Bit,
#                  RegDst: Bit,
#                  # from data
#                  pc_inc: AddrT
#                  read_data_1: DataT,
#                  read_data_2: DataT,
#                  extend_data: DataT,
#                  write_idx_1: IdxT,
#                  write_idx_2: IdxT,
#     ) -> ExecOut:







#     exec(
#         isa_py.BitVector[2](1),
#         isa_py.Bit(1),
#         isa_py.Bit(1),
#         
#         isa_py.AddrT(1),
#         isa_py.DataT(1),
#         isa_py.DataT(1),
#         isa_py.DataT(1),
#         isa_py.IdxT(1),
#         isa_py.IdxT(1),
#     )
        
    result=fetch(
        isa_py.AddrT(8),
        isa_py.Bit(1),
        )
    print(result); 

    result=fetch(
        isa_py.AddrT(8),
        isa_py.Bit(1),
        )
    print(result); 



    assert 0

#         # AddrT = DataT = BitVector[32]
# 
#     # flag = self.flag(flag_next, family.Bit(1))
#     
#     Cpu = CPU()
# 
#     # @name_outputs(out=Word, pc_next=Word)
#     a = isa_py.Word(0)
#     b = ~a
# 
#     pc_init = isa_py.Word(0)
# 
#     out, pc = cpu(isa_py.NOR, a, a, pc_init)
# 
#     assert pc == pc_init + 4
#     assert out == isa_py.Word(-1)
# 
#     out, pc = cpu(isa_py.JMP, a, b, pc)
# 
#     assert pc == b
#     assert out == 0
# 
#     out, pc = cpu(isa_py.NOR, a, b, pc)
# 
#     assert pc == b + 4
#     assert out == 0
# 
#     out, pc = cpu(isa_py.JMP, a, b, pc)
# 
#     assert pc == a
#     assert out == 0
