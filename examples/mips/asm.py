from .isa import ISA_fc

isa = ISA_fc.Py


ASM_TEMPLATE = '''\
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


for inst_name, suffix in (
        ('ADD', 'U'),
        ('AND', ''),
        ('OR', ''),
        ('XOR', ''),
        ('SLT', ''),
        ('SLT', 'U'),
        ):

    f_str = ASM_TEMPLATE.format(
            INST_NAME=inst_name,
            SUFFIX=suffix,
        )

    exec(f_str)
