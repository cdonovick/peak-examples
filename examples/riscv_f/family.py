
from peak import family

from ast_tools.passes import remove_asserts


# A bit of hack putting the def of word and idx here
# and not isa but it makes life easier
class _RiscFamily_mixin:
    @property
    def Word(self):
        return self.BitVector[32]

    @property
    def Idx(self):
        return self.BitVector[5]


class PyFamily(_RiscFamily_mixin, family.PyFamily):
    def get_register_file(fam_self, n_ports):
        class RegisterFile:
            def __init__(self):
                self.rf = {fam_self.Idx(i): fam_self.Word(0) for i in range(1 << fam_self.Idx.size)}

            def _load(self, idx):
                if not isinstance(idx, fam_self.Idx):
                    raise TypeError(idx)
                return self.rf[idx]

            def store(self, idx, value):
                if not isinstance(idx, fam_self.Idx):
                    raise TypeError(idx)
                elif not isinstance(value, fam_self.Word):
                    raise TypeError(value)
                elif idx != 0:
                    self.rf[idx] = value

        for i in range(1, n_ports+1):
            setattr(RegisterFile, f'load{i}', RegisterFile._load)

        return RegisterFile


class SMTFamily(_RiscFamily_mixin, family.SMTFamily):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._passes = remove_asserts(), *self._passes
    def get_register_file(fam_self, n_ports):
        def _make_load(cls, i):
            def load(self, idx):
                if not isinstance(idx, fam_self.Idx):
                    raise TypeError(f'{idx}::{type(idx)}, expected {fam_self.Idx}')
                return (idx != fam_self.Idx(0)).ite(self.rs[i-1], fam_self.Word(0))
            setattr(cls, f'load{i}', load)

        def _make_set(cls, i):
            def _set_rs_(self, val):
                self.rs[i-1] = val
            setattr(cls, f'_set_rs{i}_', _set_rs_)

        class RegisterFile:
            def __init__(self):
                self.rs = [fam_self.Word() for _ in range(n_ports)]
                self.rd = fam_self.Word()


            def store(self, idx, value):
                if not isinstance(idx, fam_self.Idx):
                    raise TypeError(idx)
                elif not isinstance(value, fam_self.Word):
                    raise TypeError(value)
                self.rd = (idx != fam_self.Idx(0)).ite(value, self.rd)

            def _set_rd_(self, val):
                self.rd = val

        for i in range(1, n_ports+1):
            _make_load(RegisterFile, i)
            _make_set(RegisterFile, i)

        return RegisterFile

