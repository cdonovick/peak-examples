import enum as pyenum
import typing as tp

from hwtypes import AbstractBitVector, AbstractBit, BitVector, Bit
from hwtypes.adt import Enum, Product, Sum, Tuple, TaggedUnion
from peak.assembler2 import AbstractAssembler

from .isa import R, I, Is, S, U, B, J, ArithInst, ShiftInst, AluInst, \
                    StoreInst, LoadInst, BranchInst, OP, OP_IMM_A, OP_IMM_S, \
                    OP_IMM, LUI, AUIPC, JAL, JALR, Branch, Load, Store, Inst



OPCODE = {
    OP     : 0b0110011,
    OP_IMM : 0b0010011,
    LUI    : 0b0110111,
    AUIPC  : 0b0010111,
    JAL    : 0b1101111,
    JALR   : 0b1100111,
    Branch : 0b1100011,
    Load   : 0b0000011,
    Store  : 0b0100011,
}

FUNC3 = {
    ArithInst : {
        ArithInst.ADD  : 0b000,
        ArithInst.SUB  : 0b000,
        ArithInst.SLT  : 0b010,
        ArithInst.SLTU : 0b011,
        ArithInst.XOR  : 0b100,
        ArithInst.OR   : 0b110,
        ArithInst.AND  : 0b111,
    },

    ShiftInst : {
        ShiftInst.SLL : 0b001,
        ShiftInst.SRL : 0b101,
        ShiftInst.SRA : 0b101,
    },

    LoadInst : {
        LoadInst.LB  : 0b000,
        LoadInst.LBU : 0b100,
        LoadInst.LH  : 0b001,
        LoadInst.LHU : 0b101,
        LoadInst.LW  : 0b010,
    },

    StoreInst : {
        StoreInst.SB : 0b000,
        StoreInst.SH : 0b001,
        StoreInst.SW : 0b010,
    },

    BranchInst : {
        BranchInst.BEQ  : 0b000,
        BranchInst.BNE  : 0b001,
        BranchInst.BLT  : 0b100,
        BranchInst.BGE  : 0b101,
        BranchInst.BLTU : 0b110,
        BranchInst.BGEU : 0b111,
    },

    # JALR is weird
    JALR : {
        JALR : 0b000
    },
}

FUNC7 = {
    ArithInst : {
        ArithInst.ADD  : 0b0000000,
        ArithInst.SUB  : 0b0100000,
        ArithInst.SLT  : 0b0000000,
        ArithInst.SLTU : 0b0000000,
        ArithInst.XOR  : 0b0000000,
        ArithInst.OR   : 0b0000000,
        ArithInst.AND  : 0b0000000,
    },

    ShiftInst : {
        ShiftInst.SLL : 0b0000000,
        ShiftInst.SRL : 0b0000000,
        ShiftInst.SRA : 0b0100000,
    },

}

FIELD_POS = {
    'opcode' : (0, 7),
    'rd'     : (7, 12),
    'func3'  : (12, 15),
    'rs1'    : (15, 20),
    'rs2'    : (20, 25),
    'func7'  : (25, 32),
}

IMM_LAYOUT = {
    I : {
        (0, 12) : (20, 32),
    },
    Is : {
        (0, 5)  : (20, 25),
    },
    S : {
        (0, 5)  : (7, 12),
        (5, 12) : (25, 32),
    },
    # there is some disconnect with manual here because they describe imm B
    # as having indices 1 ... 12 instead of 0 ... 11
    B : {
        (0, 4)   : (8, 12),
        (4, 10)  : (25, 31),
        (10, 11) : (7, 8),
        (11, 12) : (31, 32),
    },
    # similar as above with indices 12 ... 31
    U : {
        (0, 20) : (12, 32),
    },
    # similar as above with indices 1 ... 20
    J : {
        (0, 10)  : (21, 31),
        (10, 11) : (20, 21),
        (11, 19) : (12, 20),
        (19, 20) : (31, 32),
    },
}


DATA_LAYOUTS = (R, I, Is, S, U, B, J)
JOINED_TYPES = (OP_IMM, AluInst)
OP_TYPES = (OP, OP_IMM_A, OP_IMM_S, LUI, AUIPC, JAL, JALR, Branch, Load, Store)
TAG_TYPES = (ArithInst, ShiftInst, BranchInst, LoadInst, StoreInst)

def _overlaps(r1, r2):
    return r1[0] < r2[1] and r2[0] < r1[1]

class BitVectorBuilder:
    def __init__(self, bv_type, width):
        self.bv_type = bv_type
        self.width = width
        self.chunks = {}
        self.set_ranges = []

    def add_chunk(self, k, v):
        assert k[0] < k[1]
        assert k[1] - k[0] == v.size, (k, v)
        assert isinstance(v, self.bv_type)
        pos = -1
        for pos, r in enumerate(self.set_ranges):
            if _overlaps(k, r):
                raise ValueError('overlapping chunk')

            if k[1] <= r[0]:
                break
        else:
            pos += 1

        self.set_ranges.insert(pos, k)
        self.chunks[k] = v
        self._attest()

    def _attest(self):
        for r1, r2 in zip(self.set_ranges, self.set_ranges[1:]):
            assert r1[1] <= r2[0], (r1, r2)

    def _fill(self):
        for r1, r2 in zip(self.set_ranges, self.set_ranges[1:]):
            assert 0 <= r1[0] < r1[1] <= r2[0] < r2[1] <= self.width


        last_upper_bound = 0
        chunks_to_add = []
        for r in self.set_ranges:
            if r[0] != last_upper_bound:
                n = r[0] - last_upper_bound
                chunk_args = (last_upper_bound, r[0]), self.bv_type[n]()
                chunks_to_add.append(chunk_args)
            last_upper_bound = r[1]

        if last_upper_bound != self.width:
            n = self.width - last_upper_bound
            chunk_args = (last_upper_bound, self.width), self.bv_type[n]()
            chunks_to_add.append(chunk_args)

        for args in chunks_to_add:
            self.add_chunk(*args)

        assert self.set_ranges[0][0] == 0
        for r1, r2 in zip(self.set_ranges, self.set_ranges[1:]):
            assert r1[1] == r2[0]

        assert self.set_ranges[-1][1] == self.width

    def materialize(self):
        self._fill()
        bv = None
        for r in self.set_ranges:
            if bv is None:
                bv = self.chunks[r]
            else:
                bv = bv.concat(self.chunks[r])
        assert bv.size == self.set_ranges[-1][1], bv
        return bv


def get_match(inst):
    for k, v in inst.value_dict.items():
        if v is not None:
            break
    else:
        raise AssertionError(f'Unreachable code, {inst} has no value')

    return k, v


class Assembler(AbstractAssembler):
    @property
    def width(self) -> int:
        if issubclass(self._isa, AbstractBitVector):
            return self._isa.size
        elif issubclass(self._isa, AbstractBit):
            return 1
        else:
            return 32

    def assemble(self, inst: 'isa', bv_type: tp.Type[AbstractBitVector] = BitVector) -> AbstractBitVector:
        if not isinstance(inst, self._isa):
            raise TypeError()
        if issubclass(self._isa, (AbstractBit ,AbstractBitVector)):
            return bv_type[self.width](inst)

        builder = BitVectorBuilder(bv_type, self.width)
        if isinstance(inst, Inst):
            _asm_Inst(inst, builder)
        elif isinstance(inst, OP_IMM):
            _asm_OP_IMM(inst, builder)
        elif isinstance(inst, OP_TYPES):
            _asm_OP(inst, builder)
        elif isinstance(inst, AluInst):
            _asm_AluInst(inst, builder, True)
        elif isinstance(inst, TAG_TYPES):
            _asm_tag(inst, builder, True)
        else:
            assert isinstance(inst, DATA_LAYOUTS)
            _asm_data(inst, builder)

        return builder.materialize()

    def disassemble(self, bv: BitVector) -> 'Type[self._isa]':
        pass

    def extract(self, bv: AbstractBitVector, field: tp.Union[str, int, type]) -> AbstractBitVector:
        pass

    def match(self, bv: AbstractBitVector, field: tp.Union[str, type]) -> AbstractBit:
        pass

    def is_valid(self, opcode: AbstractBitVector) -> AbstractBit:
        pass

    def from_fields(self, *args, **kwargs) -> AbstractBitVector:
        pass

def _asm_Inst(inst, builder):
    assert isinstance(inst, Inst)
    op_t, value = get_match(inst)
    assert isinstance(value, op_t)
    bv_type = builder.bv_type
    builder.add_chunk(FIELD_POS['opcode'], bv_type[7](OPCODE[op_t]))


    if isinstance(value, TaggedUnion):
        assert isinstance(value, OP_IMM)
        _asm_OP_IMM(value, builder)
    else:
        assert isinstance(value, OP_TYPES)
        _asm_OP(value, builder)

def _asm_OP_IMM(inst, builder):
    _, value = get_match(inst)
    assert isinstance(value, OP_TYPES)
    _asm_OP(value, builder)

def _asm_OP(inst, builder):
    assert isinstance(inst, Product)
    assert hasattr(inst, 'data')
    op_t = type(inst)
    has_func7 = op_t is OP_IMM_S or op_t is OP

    if hasattr(inst, 'tag'):
        tag = inst.tag
        if isinstance(tag, TaggedUnion):
            assert isinstance(tag, AluInst)
            _asm_AluInst(tag, builder, has_func7)
        else:
            assert isinstance(tag, TAG_TYPES)
            _asm_tag(tag, builder, has_func7)
    elif isinstance(inst, JALR):
        # JALR is weird
        _asm_tag(inst, builder, has_func7)

    data = inst.data
    assert isinstance(data, DATA_LAYOUTS)
    _asm_data(data, builder)

def _asm_AluInst(inst, builder, has_func7):
    _, tag  = get_match(inst)
    assert isinstance(tag, TAG_TYPES)
    _asm_tag(tag, builder, has_func7)

def _asm_tag(inst, builder, has_func7):
    tag_t = type(inst)
    func3 = FUNC3.get(tag_t, {}).get(inst, None)
    bv_type = builder.bv_type
    if func3 is not None:
        builder.add_chunk(FIELD_POS['func3'], bv_type[3](func3))

    if has_func7:
        func7 = FUNC7.get(tag_t, {}).get(inst, None)
        if func7 is not None:
            builder.add_chunk(FIELD_POS['func7'], bv_type[7](func7))

def _asm_data(inst, builder):
    assert isinstance(inst, Product)
    data_t = type(inst)

    for k, v in inst.value_dict.items():
        assert isinstance(v, AbstractBitVector)
        if k == 'imm':
            for imm_slice, pos in IMM_LAYOUT[data_t].items():
                builder.add_chunk(pos, v[slice(*imm_slice)])
        else:
            builder.add_chunk(FIELD_POS[k], v)
