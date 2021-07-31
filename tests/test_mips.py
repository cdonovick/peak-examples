import functools
import itertools
import operator
import random

import pytest

from examples.mips import sim, isa as isa_, family, asm


NTESTS = 16

GOLD = {
        'ADDU': operator.add,
        'AND': operator.and_,
        'OR': operator.or_,
        'XOR': operator.xor,
        'SLT': lambda a, b: type(a)(a.bvslt(b)),
        'SLTU': lambda a, b: type(a)(a.bvult(b)),
}



@pytest.mark.parametrize('op_name', GOLD.keys())
@pytest.mark.parametrize('use_imm', (False, True))
def test_mips(op_name, use_imm):
    MIPS_py = sim.MIPS32_fc.Py
    isa = isa_.ISA_fc.Py

    mips_py = MIPS_py()
    for i in range(1, 32):
        mips_py.register_file.store(isa.Idx(i), isa.Word(i))


    asm_f = getattr(asm, f'asm_{op_name}')
    for _ in range(NTESTS):
        rd = isa.Idx(random.randrange(1, 1 << isa.Idx.size))
        rs = isa.Idx(random.randrange(1, 1 << isa.Idx.size))
        if use_imm:
            im = random.randrange(0, 1 << 5)
            inst = asm_f(rd=rd, rs=rs, im=im)
            a = mips_py.register_file.load1(rs)
            b = isa.Word(im)
        else:
            rt = isa.Idx(random.randrange(1, 1 << isa.Idx.size))
            inst = asm_f(rd=rd, rs=rs, rt=rt)
            a = mips_py.register_file.load1(rs)
            b = mips_py.register_file.load1(rt)

        acc = isa.BitVector[64](random.randrange(0, 1 << isa.Word.size*2))
        acc_next = mips_py(inst, acc)
        assert GOLD[op_name](a, b) == mips_py.register_file.load1(rd)
        assert acc == acc_next
