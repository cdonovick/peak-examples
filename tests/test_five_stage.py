from examples.five_stage.sim import Top, isa

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
