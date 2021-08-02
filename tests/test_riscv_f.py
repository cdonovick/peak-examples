
from peak.mapper import ArchMapper, RewriteRule
from examples.riscv_f import family as riscv_family
from examples.riscv_f import sim as riscv_sim


def test_smt():
    arch_fc = riscv_sim.R32I_mappable_fc
    arch_mapper = ArchMapper(arch_fc, family=riscv_family)
