from ast_tools.passes import remove_asserts

from peak import family


class _Family_mixin:
    @property
    def Idx(self):
        return self.BitVector[2]

    @property
    def Word(self):
        return self.BitVector[16]

    @property
    def DWord(self):
        return self.BitVector[32]



class PyFamily(_Family_mixin, family.PyFamily):
    def get_register_file(fam_self):
        class RegisterFile:
            def __init__(self):
                self.rf = {}

            def _load(self, idx):
                return self.rf[idx]

            load1 = _load
            load2 = _load

            def store(self, idx, value):
                self.rf[idx] = value

        return RegisterFile

class SMTFamily(_Family_mixin, family.SMTFamily):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._passes = remove_asserts(), *self._passes

    def get_register_file(fam_self):
        class RegisterFile:
            def __init__(self):
                self.rs1 = fam_self.DWord()
                self.rs2 = fam_self.DWord()
                self.rd  = fam_self.DWord()

            def load1(self, idx):
                return self.rs1

            def load2(self, idx):
                return self.rs2

            def store(self, idx, value):
                self.rd = value

            def _set_rs1_(self, val):
                self.rs1 = val

            def _set_rs2_(self, val):
                self.rs2 = val

        return RegisterFile

