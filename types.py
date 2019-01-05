import sys

def identity(x):
    return x

def from_base(digits, base = 2):
    num = 0
    power = 0
    for digit in digits:
        num += digit * base ** power
        power += 1
    return num

def to_base(num, base = 2):
    digits = []
    while num:
        num, digit = divmod(num, base)
        digits.append(digit)
    return digits[::-1]

class Base:
    def __init__(self, type_ = None):
        self.base_type = type_
        self.attrs = {'Identity': (1, identity), 'Convert': (1, self.base_type)}

    def add_method(self, attr_name, attr_fn, attr_arity):
        self.attrs[attr_name] = (attr_arity, attr_fn)

class BinaryBase:
    def __init__(self, value = None):
        if isinstance(value, int):
            self.value = to_base(value, base = 2)
            
        elif isinstance(value, (list, str)):
            if isinstance(value, str):
                value = list(map(int, str))
                
            if all(v in (0, 1) for v in value):
                self.value = value
            else:
                value = from_base(value, base = max(value) + 1)
                self.value = to_base(value, base = 2)

        else:
            raise TypeError('Invalid type: \'{}\''.format(type(value)))

        del value

    def from_binary(self):
        return from_base(self.value, base = 2)

class InputBase:
    def __init__(self, file = sys.stdin):
        self.file = file
        self.text = self.file.read()
        self.iter = iter(self.text)

class OutputBase:
    def __init__(self, file = sys.stdout):
        self.file = file
        self.last = ''
        self.written = ''

class UniqueBase:
    def __init__(self, value = None):
        self.value = []
        if not hasattr(value, '__iter__'):
            

Array           = Base(list)
Binary          = Base(BinaryBase)
Boolean         = Base(bool)
Complex         = Base(complex)
FloatingPoint   = Base(float)
InputSystem     = Base(InputBase)
Integer         = Base(int)
Mapping         = Base(dict)
OutputSystem    = Base(OutputBase)
SetArray        = Base(set)
StringArray     = Base(str)
UniqueArray     = Base(UniqueBase)














