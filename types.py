import cmath
import math
import operator
import sys

def identity(x):
    return x

def is_prime(a):
    for i in range(2, int(a ** 0.5)+1):
        if a%i:
            continue
        return False
    return True

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

def gaussian_prime(z):
    a, b = int(z.real), int(z.imag)
    if a == 0:
        return b % 4 == 3 and is_prime(b)
    elif b == 0:
        return a % 4 == 3 and is_prime(a)
    else:
        return is_prime(a ** 2 + b ** 2)

def read_int():
    text = ''
    while True:
        char = sys.stdin.read(1)
        if char in ('123456789' + ('0' * bool(text))):
            text += char
        else:
            if text:
                return int(text) 

class Base:
    def __init__(self, type_ = None):
        self.base_type = type_
        self.attrs = {'Identity': (1, identity, False), 'Convert': (1, self.base_type, False)}

    def add_method(self, attr_name, attr_fn, attr_arity, verify = True):
        self.attrs[attr_name] = (attr_arity, attr_fn, verify)

    def call_method(self, method, *args):
        if method in self.attrs.keys():
            arity, fun, verif = self.attrs[method]

            if verif:
                for arg in args:
                    if not isinstance(arg, self.base_type):
                        raise TypeError
                    
            if arity == len(args):
                return fun(*args)
            if arity == -1:
                return fun(*args)
            raise TypeError
        raise KeyError

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

class FunctionBase:
    def __init__(self, value):
        self.value = value

class InputBase:
    def __init__(self, file = sys.stdin):
        self.file = file
        self.text = self.file.read()
        self.iter = iter(self.text)

class MatrixBase:
    def __init__(self, rows, columns):
        self.value = []
        for i in range(rows):
            temp = []
            for j in range(columns):
                temp.append(int(i == j))
            self.value.append(temp.copy())
            temp.clear()

    def set_value(self, row, column, value):
        self.value[row - 1][column - 1] = value
        return self.value

    def set_row(self, row, values):
        values = list(values)
        self.value[row - 1] = values
        return self.value

    def set_column(self, column, values):
        values = list(values)
        column -= 1
        copy = []
        for row in self.value:
            row[column] = values.pop(0)
            copy.append(row.copy())
        self.value = copy.copy()
        return self.value

class OutputBase:
    def __init__(self, file = sys.stdout):
        self.file = file
        self.last = ''
        self.written = ''

class UniqueBase:
    def __init__(self, value = None):
        self.value = []
        if not hasattr(value, '__iter__'):
            raise TypeError
        for elem in value:
            if elem not in self.value:
                self.value.append(elem)

Array           = Base(list)
Binary          = Base(BinaryBase)
Boolean         = Base(bool)
Complex         = Base(complex)
FloatingPoint   = Base(float)
InputSystem     = Base(InputBase)
Integer         = Base(int)
Mapping         = Base(dict)
Matrix          = Base(MatrixBase)
OutputSystem    = Base(OutputBase)
SetArray        = Base(set)
StringArray     = Base(str)
UniqueArray     = Base(UniqueBase)

ExtendedFunctionSet = Base(FunctionBase)

Array.add_method('AppendElement', lambda a, b: a + [b], 2, verify = False)
Array.add_method('AppendElements', lambda a, *b: a + list(b), 2, verify = False)
Array.add_method('ExtractElementFromIndex', lambda a, b: a.pop(b), 2, verify = False)
Array.add_method('FindElementAtIndex', lambda a, b: a[b], 2, verify = False)
Array.add_method('FindIndexOfElement', lambda a, b: a.index(b), 2, verify = False)
Array.add_method('CountOccurencesOfElement', lambda a, b: a.count(b), 2, verify = False)
Array.add_method('ReverseArray', lambda a: list(reversed(a)), 1)
Array.add_method('SortArrayAscending', sorted, 1)
Array.add_method('SortArrayDescending', lambda a: sorted(a, reverse = True), 1)
Array.add_method('SortArrayByKeyFunction', lambda a, k: sorted(a, key = k), 2, verify = False)

Binary.add_method('Increment', lambda a: BinaryBase(a.from_binary() + 1), 1)
Binary.add_method('Decrement', lambda a: BinaryBase(a.from_binary() - 1), 1)
Binary.add_method('ConvertFromBinaryToInteger', lambda a: a.from_binary(), 1)
Binary.add_method('BinarySum', lambda a, b: BinaryBase(a.from_binary() + b.from_binary()), 2)
Binary.add_method('BinaryDifference', lambda a, b: BinaryBase(a.from_binary() - b.from_binary()), 2)
Binary.add_method('BinaryProduct', lambda a, b: BinaryBase(a.from_binary() * b.from_binary()), 2)

Boolean.add_method('LogicalAnd', lambda a, b: a and b, 2)
Boolean.add_method('LogicalOr', lambda a, b: a or b, 2)
Boolean.add_method('LogicalNot', lambda a: not a, 1)
Boolean.add_method('BitwiseAnd', lambda a, b: a & b, 2)
Boolean.add_method('BitwiseOr', lambda a, b: a | b, 2)
Boolean.add_method('BitwiseXor', lambda a, b: a ^ b, 2)
Boolean.add_method('BitwiseNot', lambda a: ~a, 1)

Complex.add_method('IncrementRealValue', lambda a: a + 1, 1)
Complex.add_method('DecrementRealValue', lambda a: a - 1, 1)
Complex.add_method('IncrementImaginaryValue', lambda a: a + 1j, 1)
Complex.add_method('DecrementImaginaryValue', lambda a: a - 1j, 1)
Complex.add_method('PhaseInRadians', cmath.phase, 1)
Complex.add_method('PhaseInDegrees', lambda a: math.degrees(cmath.phase(a)), 1)
Complex.add_method('Modulus', abs, 1)
Complex.add_method('ExpressInPolarCoordinateForm', cmath.polar, 1)
Complex.add_method('ExpressInRectangularCoordinateForm', cmath.rect, 1)
Complex.add_method('GaussianPrimality', gaussian_prime, 1)

InputSystem.add_method('ReadLineOfInput', input, 0)
InputSystem.add_method('ReadEvaluatedLineOfInput', lambda: eval(input()), 0)
InputSystem.add_method('ReadCharacterOfInput', lambda: sys.stdin.read(1), 0)
InputSystem.add_method('ReadIntegerFromInput', read_int, 0)
InputSystem.add_method('ExhaustRemainingInput', sys.stdin.read, 0)

Integer.add_method('AbsoluteDifference', lambda a, b: abs(a - b), 2)
Integer.add_method('Primality', lambda a: is_prime(a), 1)

Matrix.add_method('Product', operator.matmul, 2)

inc = lambda a: a + 1
dec = lambda a: a - 1

data = zip(['Increment', 'Decrement', 'Sum', 'Difference', 'Product', 'Quotient', 'Exponentiation', 'RemainderDivision'],
           [inc, dec, sum, operator.sub, operator.mul, operator.floordiv, pow, operator.mod],
           [1, 1, -1, 2, 2, 2, 2, 2])

for name, fun, arity in data:
    Integer.add_method(name, fun, arity)
    FloatingPoint.add_method(name, fun, arity)
    if name not in ['Increment', 'Decrement']:
        Complex.add_method(name, fun, arity)

Matrix.attrs['Convert'] = (2, Matrix.base_type, False)



