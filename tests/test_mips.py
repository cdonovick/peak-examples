import functools
import itertools
import operator
import random

import pytest

from hwtypes import BitVector
from peak.mapper import ArchMapper, RewriteRule

from examples.mips import sim, isa as isa_, family, asm
from examples.mips.util import clo, clz


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

    asm_f = getattr(asm, f'asm_{op_name}')

    mips_py = MIPS_py()
    for i in range(1, 32):
        mips_py.register_file.store(isa.Idx(i), isa.Word(i))


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


def test_mips_smt():
    arch_fc = sim.MIPS32_mappable_fc
    arch_mapper = ArchMapper(arch_fc, family=family)


def _gold_cl(f, x):
    T = type(x)
    cnt = T(0)
    for i in range(x.size):
        if f(x[x.size - i - 1]):
            return cnt
        cnt += 1
    return T(cnt)

def _test_eq(x, *args):
    for r in args:
        assert type(x) == type(r)

    for (x, y) in zip(args, args[1:]):
        assert x == y

clo_gold = functools.partial(_gold_cl, lambda x: ~x)
clz_gold = functools.partial(_gold_cl, lambda x: x)

@pytest.mark.parametrize('size', (1 << k for k in range(8)))
def test_cl(size):
    for _ in range(NTESTS):
        x = BitVector.random(size)

        lo = clo(x)
        lzn = clz(~x)
        log = clo_gold(x)
        lzgn = clz_gold(~x)
        _test_eq(x, lo, lzn, log, lzgn)

        lon = clo(~x)
        lz = clz(x)
        logn = clo_gold(~x)
        lzg = clz_gold(x)
        _test_eq(x, lon, lz, logn, lzg)

GOLD_CL = {
    'CLO': clo_gold,
    'CLZ': clz_gold,
}

@pytest.mark.parametrize('op_name', GOLD_CL.keys())
def test_mips_cl(op_name):
    MIPS_py = sim.MIPS32_fc.Py
    isa = isa_.ISA_fc.Py

    mips_py = MIPS_py()
    for i in range(1, 32):
        mips_py.register_file.store(isa.Idx(i), isa.Word(i))


    asm_f = getattr(asm, f'asm_{op_name}')
    for _ in range(NTESTS):
        rd = isa.Idx(random.randrange(1, 1 << isa.Idx.size))
        rs = isa.Idx(random.randrange(1, 1 << isa.Idx.size))
        inst = asm_f(rd=rd, rs=rs)
        a = mips_py.register_file.load1(rs)
        acc = isa.BitVector[64](random.randrange(0, 1 << isa.Word.size*2))
        acc_next = mips_py(inst, acc)
        assert GOLD_CL[op_name](a) == mips_py.register_file.load1(rd)
        assert acc == acc_next
