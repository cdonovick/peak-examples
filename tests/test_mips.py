import functools
import itertools
import operator
import random

import pytest

from examples.mips import sim, isa, family


def test_mips():
    MIPS_py = sim.MIPS32_fc.Py
    MIPS_smt = sim.MIPS32_fc.SMT
