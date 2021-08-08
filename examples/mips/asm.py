from .isa import ISA_fc

isa = ISA_fc.Py


ASM_TEMPLATE_RI = '''\
def asm_{INST_NAME}{SUFFIX}(rd, rs, rt=None, im=None):
    if rt is not None and im is not None:
        raise ValueError('May not specify both rt and imm')
    elif rt is None and im is None:
        raise ValueError('Must specify either rt or imm')

    rd = isa.Idx(rd)
    rs = isa.Idx(rs)

    if rt is not None:
        rt = isa.Idx(rt)
        op = isa.R3Inst.{INST_NAME}{SUFFIX}
        inst = isa.R3(rd, rs, rt, op)
    else:
        im = isa.Imm(im)
        op = isa.I2Inst.{INST_NAME}I{SUFFIX}
        inst = isa.I2(rd, rs, im, op)

    return isa.Inst(inst)
'''

_NAME_SUFFIX = (
    ('ADD', 'U'),
    ('AND', ''),
    ('OR', ''),
    ('XOR', ''),
    ('SLT', ''),
    ('SLT', 'U'),
)

for inst_name, suffix in _NAME_SUFFIX:
    f_str = ASM_TEMPLATE_RI.format(
        INST_NAME=inst_name,
        SUFFIX=suffix,
    )

    exec(f_str)

ASM_TEMPLATE_R = '''\
def asm_{INST_NAME}(rd, rs, rt):
    rd = isa.Idx(rd)
    rs = isa.Idx(rs)
    rt = isa.Idx(rt)
    op = isa.R3Inst.{INST_NAME}
    inst = isa.R3(rd, rs, rt, op)
    return isa.Inst(inst)
'''


_DONE = {''.join(ns) for ns in _NAME_SUFFIX}
for inst_name in isa.R3Inst._field_table_:
    if inst_name in _DONE:
        continue

    f_str = ASM_TEMPLATE_R.format(INST_NAME=inst_name)
    exec(f_str)

ASM_TEMPLATE_R2 = '''\
def asm_{INST_NAME}(rd, rs):
    rd = isa.Idx(rd)
    rs = isa.Idx(rs)
    op = isa.R2Inst.{INST_NAME}
    inst = isa.R2(rd, rs, op)
    return isa.Inst(inst)
'''

for inst_name in isa.R2Inst._field_table_:

    f_str = ASM_TEMPLATE_R2.format(INST_NAME=inst_name)
    exec(f_str)
