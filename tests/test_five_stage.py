from examples.five_stage.sim import Top, isa

def test_five_stage():
    isa = isa.Py

    Exec = Top.Py

    exec = Exec()

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




    exec(
        isa.BitVector[2](1),
        isa.Bit(1),
        isa.Bit(1),
        
        isa.AddrT(1),
        isa.DataT(1),
        isa.DataT(1),
        isa.DataT(1),
        isa.IdxT(1),
        isa.IdxT(1),
        isa.IdxT(1),
    )
        

#         # AddrT = DataT = BitVector[32]
# 
#     # flag = self.flag(flag_next, family.Bit(1))
#     
#     Cpu = CPU()
# 
#     # @name_outputs(out=Word, pc_next=Word)
#     a = isa.Word(0)
#     b = ~a
# 
#     pc_init = isa.Word(0)
# 
#     out, pc = cpu(isa.NOR, a, a, pc_init)
# 
#     assert pc == pc_init + 4
#     assert out == isa.Word(-1)
# 
#     out, pc = cpu(isa.JMP, a, b, pc)
# 
#     assert pc == b
#     assert out == 0
# 
#     out, pc = cpu(isa.NOR, a, b, pc)
# 
#     assert pc == b + 4
#     assert out == 0
# 
#     out, pc = cpu(isa.JMP, a, b, pc)
# 
#     assert pc == a
#     assert out == 0
