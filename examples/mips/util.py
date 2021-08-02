from hwtypes import modifiers

Initial = modifiers.make_modifier('Initial', cache=True)

def _clo(x):
    if x.size == 1:
        return x
    else:
        half_size = x.size >> 1
        assert (half_size << 1) == x.size
        top = _clo(x[half_size:]).zext(1)
        bot = _clo(x[:half_size]).zext(1)
        return (top == half_size).ite(top + bot, top)

def clo(x):
    if (x.size & (x.size - 1)) != 0:
        raise TypeError(f'clo only works on bitvectors with power of 2 width')
    lo = _clo(x)
    # k.bit_length() returns number of bits necesary to represent k
    assert lo.size == x.size.bit_length()
    return lo.zext(x.size - lo.size)

def clz(x):
    if (x.size & (x.size - 1)) != 0:
        raise TypeError(f'clz only works on bitvectors with power of 2 width')
    return clo(~x)
