import cmath
import math
import functools
import itertools
import operator
import sys

import _exceptions as exceptions

def identity(x):
    return x

def is_prime(a):
    for i in range(2, int(a ** 0.5)+1):
        if a%i:
            continue
        return False
    return a > 1 and isinstance(a, int)

def from_base(digits, base = 2):
    num = 0
    power = 0
    for digit in digits[::-1]:
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

def read_int(in_text):
    text = ''
    while True:
        try: char = next(in_text)
        except StopIteration: break
        if char in ('123456789' + ('0' * bool(text))):
            text += char
        else:
            if text:
                return int(text)
    return 0

def flatten(array):
    flat = []
    for elem in array:
        if isinstance(elem, list):
            flat += flatten(elem)
        else:
            flat.append(elem)
    return flat

def zipwith(left, right, func):
    final = []
    for lelem, relem in zip(left, right):
        final.append(func(lelem, relem))
    return final

def next_prime(current):
    while True:
        current += 1
        if is_prime(current):
            return current

def prime_factors(num):
    factors = []
    prime = 2
    while num > 1:
        if num % prime:
            prime = next_prime(prime)
        else:
            num //= prime
            factors.append(prime)
    return factors

def prime_exponents(num):
    facts = prime_factors(num)
    max_prime = max(facts)
    primes = {i+1:0 for i in range(max_prime) if is_prime(i+1)}

    while facts:
        primes[facts.pop()] += 1
    return list(primes.values())

def from_exponents(pows):
    powers = pows.copy()
    total = 1
    prime = 2
    while powers:
        total *= prime ** powers.pop(0)
        prime = next_prime(prime)
    return total

def find_base_type(value):
    for t in TYPES:
        if type(value) == t.base_type:
            return t
    exceptions.RaiseException('TypeError: Unknown type: {}'.format(type(value)))

class Base:
    def __init__(self, type_ = None, name = ''):
        self.base_type = type_
        self.type_name = name
        self.attrs = {'Identity': (1, identity, False)}

    def add_method(self, attr_name, attr_fn, attr_arity, verify = True, convert = True):
        self.attrs[attr_name] = (attr_arity, attr_fn, verify, convert)

    def call_method(self, method, *args):
        if method in self.attrs.keys():
            arity, fun, verif, conv = self.attrs[method]
            
            if verif in (True, False):
                cont = int(verif)
                verif = self.base_type
            elif isinstance(verif, tuple):
                cont = 2
            else:
                cont = 1

            if cont == 1:
                for i, arg in enumerate(args):
                    if not isinstance(arg, verif):
                        try:
                            args[i] = verif(arg)
                        except:
                            exceptions.RaiseException('TypeError: Argument type mismatch when running \'{}:{}\''.format(self.type_name, method))

            elif cont == 2:
                for i, arg in enumerate(args):
                    if not isinstance(arg, verif[i]):
                        try:
                            args[i] = verif[i](arg)
                        except:
                            exceptions.RaiseException('TypeError: Argument type mismatch when running \'{}:{}\''.format(self.type_name, method))

            if arity == len(args) or arity == -1:
                ret = fun(*args)
                if not conv:
                    return ret
                to_type = find_base_type(ret)
                return to_type.call_method('Convert', ret)
            
            exceptions.RaiseException('TypeError: Incorrect number of arguments. Expected {} but received {}'.format(arity, len(args)))
        
        exceptions.RaiseException('KeyError: Unknown method \'{}\''.format(method))

class BinaryBase:
    def __init__(self, value = None):
        if isinstance(value, int):
            self.value = to_base(value, base = 2)
            
        elif isinstance(value, (list, str)):
            if isinstance(value, str):
                value = list(map(int, value))

            while value[0] == 0:
                value.pop(0)
                
            if all(v in (0, 1) for v in value):
                self.value = value
            else:
                value = from_base(value, base = max(value) + 1)
                self.value = to_base(value, base = 2)

        elif isinstance(value, BinaryBase):
            self.value = value.value

        else:
            exceptions.RaiseException('TypeError: Invalid type \'{}\''.format(type(value)))

        del value

    def __repr__(self):
        return 'b' + ''.join(map(str, self.value))

    def __invert__(self):
        new = []
        for bit in self.value:
            new.append(bit ^ 1)
        return BinaryBase(new)

    def from_binary(self):
        return from_base(self.value, base = 2)

class ConstantsBase:
    def __init__(self, type_choice):
        if type_choice == int:
            self.constant_list = 'integers'
        if type_choice == float:
            self.constant_list = 'floats'
        if type_choice == str:
            self.constant_list = 'strings'

class FunctionBase:
    def __init__(self, value):
        self.value = value

class InputBase:
    def __init__(self, file = sys.stdin, argv = sys.argv[1:]):
        self.filename = file
        if file == 'DEFAULT':
            file = sys.stdin
        elif isinstance(file, str):
            file = open(file)

        self.file = file
        self.text = self.file.read()
        self.iter = iter(self.text)
        self.lines = iter(self.text.split('\n'))
        self.argv = iter(argv)

    def __repr__(self):
        return 'InputBase<{}>'.format(self.filename)

    def read_line(self):
        try:
            return next(self.lines)
        except StopIteration:
            self.lines = iter(self.text.split('\n'))
            return next(self.lines)

    def read_eval(self):
        return eval(self.read_line())

    def read_char(self):
        try:
            return next(self.iter)
        except StopIteration:
            self.iter = iter(self.text)
            return next(self.iter)

    def read_int(self):
        return read_int(iter(self.text))

    def read_rest(self):
        return ''.join(self.iter)

    def read_intchar(self):
        return ord(self.read_char())

    def read_argv(self):
        try:
            return next(self.argv)
        except StopIteration:
            self.argv = iter(sys.argv[1:])
            return next(self.argv)

class MatrixBase:
    def __init__(self, arg, second = None, zero = False):
        self.next_row = 1
        self.next_column = 1
        
        if second is None:
            self.value = arg
            self.rows = len(arg)
            self.columns = len(arg[0]) if arg else 0
            self.dims = [self.rows, self.columns]
            
        else:
            rows = arg
            columns = second
            self.value = []
            self.rows = rows
            self.columns = columns
            self.dims = [rows, columns]
            
            for i in range(rows):
                temp = []
                for j in range(columns):
                    temp.append(int(i == j) * (not zero))
                self.value.append(temp.copy())
                temp.clear()

    def __repr__(self):
        out = '('
        for row in self.value:
            out += ' '.join(list(map(str, row))).join('()')
        return out + ')'

    def __eq__(self, other):
        if not isinstance(other, MatrixBase):
            exceptions.RaiseException('TypeError: Unable to equate a Matrix to a non-Matrix type')
        
        for i in range(self.rows):
            for j in range(self.columns):
                if self.get_value(i, j) != other.get_value(i, j):
                    return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def set_value(self, row, column, value):
        copy = self.value.copy()
        copy[row - 1][column - 1] = value
        return copy

    def set_row(self, row, values):
        values = list(values)
        copy = self.value.copy()
        copy[row - 1] = values
        return copy

    def set_column(self, column, values):
        values = list(values)
        column -= 1
        copy = []
        for row in self.value:
            row[column] = values.pop(0)
            copy.append(row.copy())
        return copy

    def get_value(self, row, column):
        return self.value[row - 1][column - 1]

    def get_row(self, row):
        return self.value[row - 1]

    def get_column(self, column):
        return [row[column - 1] for row in self.value]

    def add_next(self, value):
        self.set_value(self.next_row, self.next_column, value)
        self.next_column += 1
        if self.next_column > self.columns:
            self.next_column = 1
            self.next_row += 1

        if self.next_row > self.rows:
            self.next_row = 1

    def mul(self, other):
        if isinstance(other, int):
            ret = MatrixBase(self.value.copy())
            for i in range(self.rows):
                for j in range(self.columns):
                    ret.set_value(i, j, other * self.get_value(i, j))
            return ret

        if not isinstance(other, MatrixBase):
            exceptions.RaiseException('TypeError: Can only multiply a Matrix by either an integer or a matrix')
        
        if self.columns != other.rows:
            exceptions.RaiseException('TypeError: Non-conformable dimensions {}x{} and {}x{}'.format(self.rows, self.columns, *other.dims))
        
        new = MatrixBase(self.rows, other.columns, zero = True)
        left = self.value.copy()
        right = other.transpose()

        while left:
            row = left.pop(0)
            for rrow in right:
                ret = 0
                for l, r in zip(row, rrow):
                    ret += l * r
                new.add_next(ret)

        return new.value.copy()

    def add(self, other):
        if self.columns != other.columns or self.rows != other.rows:
            exceptions.RaiseException('TypeError: Non-conformable dimensions {}x{} and {}x{}'.format(self.rows, self.columns, *other.dims))
        
        ret = MatrixBase(*self.dims, zero = True)
        for i in range(self.rows):
            for j in range(self.columns):
                sum_ = self.get_value(i, j) + other.get_value(i, j)
                ret.set_value(i, j, sum_)
        return ret

    def sub(self, other):
        return self.add(other.neg())

    def pow(self, other):
        ret = MatrixBase(self.value.copy())
        for i in range(other - 1):
            ret *= self
        return ret

    def neg(self):
        ret = MatrixBase(self.value.copy())
        for i in range(self.rows):
            for j in range(self.columns):
                ret.set_value(i, j, -self.get_value(i, j))
        return ret

    def det(self):
        if self.rows == 1 == self.columns:
            return self.value[0][0]

        if self.rows == self.columns:
            mat = self.value.copy()
            det = 0
            for i, row in enumerate(mat):
                copy = mat.copy()
                copy.pop(i)
                copy = MatrixBase([r[1:] for r in copy])
                det += row[0] * copy.det() * (-1) ** i
            return det

        other = MatrixBase(self.transpose())
        return MatrixBase(self.mul(other)).det() ** 0.5

    def minor(self, i, j):
        copy = []
        for each in self.value.copy():
            copy.append(each.copy())
        copy.pop(i - 1)
        minor_mat = []
        for k, row in enumerate(copy):
            row.pop(j - 1)
            minor_mat.append(row)
        minor_mat = MatrixBase(minor_mat)
        return minor_mat.det()

    def cofactor(self, i, j):
        return self.minor(i, j) * (-1) ** (i + j)

    def adjugate(self):
        adj = MatrixBase(self.rows, self.columns)
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                adj.set_value(i, j, self.cofactor(i, j))
        return adj.transpose()

    def inverse(self):
        det = self.det()
        adj = self.adjugate()
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                adj.set_value(i, j, adj.get_value(i, j) / det)
        return adj

    def transpose(self):
        new = [[] for _ in range(self.columns)]
        for row in self.value:
            for index, elem in enumerate(row):
                new[index].append(elem)
        return MatrixBase(new)
    
    def reshape(self, rows, columns):
        new = MatrixBase(rows, columns, zero = True)
        values = flatten(self.value)
        while values:
            new.add_next(values.pop(0))
        return new
    
class OutputBase:
    def __init__(self, file = sys.stdout):
        if file == 'DEFAULT':
            file = sys.stdout
        if file == 'ERROR':
            file = sys.stderr
            
        self.file = file
        self.last = ''
        self.written = ''
        self.heldback = None

    def __repr__(self):
        return 'OutputBase<{}>'.format('DEFAULT' if self.file == sys.stdout else 'ERROR')

    def print(self, text, sep = ' ', end = '\n', ret = False):
        init_text = text
        if isinstance(text, list):
            text = sep.join(map(str, text))

        text = str(text)
        self.last = text + str(end)
        self.written += self.last

        if self.heldback is None:
            print(text, end = str(end), file = self.file)

        else:
            self.heldback += self.last

        if ret:
            return text

    def chr_print(self, integers):
        self.print(''.join(map(chr, integers)))

    def flush(self):
        print(self.heldback)
        self.heldback = None

    def holdback(self):
        self.heldback = ''

class UniqueBase:
    def __init__(self, value = None):
        self.value = []
        if not hasattr(value, '__iter__'):
            raise TypeError
        for elem in value:
            if elem not in self.value:
                self.value.append(elem)

class RecurringDecimal:
    def __init__(self, value, repeat):
        self.power = 10 ** -(len(str(value)) - int(value < 0) - str(value).count('.'))
        self.const = value
        self.repeat = repeat
        self.cut = 15 // (len(str(self.repeat)) + 1)

    def __repr__(self):
        if self.const == 0:
            out = '0.'
        else:
            out = str(self.const)
            
        count = len(out.split('.')[1])
        while count < 7:
            out += str(self.repeat)
            count = len(out.split('.')[1])
            
        return out + '...'

    def rationalize(self):
        left = self.const
        power = self.power
        for i in range(10):
            left += self.repeat * power
            power *= 0.1
        return left

    def to_recurr(self, ret):
        found = zipwith(ret, ret[1:], operator.eq)
        repeat = ret[found.index(True)]
        const = ret[:found.index(True)]
        return RecurringDecimal(float(const), int(repeat))

    def __add__(self, other):
        if type(self) == type(other):
            ret = self.rationalize() + other.rationalize()
        else:
            ret = self.rationalize() + other
        ret = str(ret)[:self.cut+1]
        return self.to_recurr(ret)

    __radd__ = __add__

def new(type_name):
    def inner(*args):
        return type_(*args)

    type_ = {
        'output': OutputBase,
        'input' : InputBase,
        'unique': UniqueBase,
    }[type_name]
    return inner

def convert(type_name):
    def inner(value):

        if type_name == 'Array':            func = list
        if type_name == 'Binary':           func = BinaryBase
        if type_name == 'Boolean':          func = bool
        if type_name == 'Complex':          func = complex
        if type_name == 'FloatingPoint':    func = float
        if type_name == 'InputSystem':      func = InputBase
        if type_name == 'Integer':          func = int
        if type_name == 'Matrix':           func = MatrixBase
        if type_name == 'OutputSystem':     func = OutputBase
        if type_name == 'SetArray':         func = set
        if type_name == 'StringArray':      func = str
        if type_name == 'UniqueArray':      func = UniqueBase

        if type(value) == func:
            return value

        return func(value)
        
    return inner

Array           = Base(list, 'Array')
Binary          = Base(BinaryBase, 'Binary')
Boolean         = Base(bool, 'Boolean')
Complex         = Base(complex, 'Complex')
FloatingPoint   = Base(float, 'FloatingPoint')
InputSystem     = Base(InputBase, 'InputSystem')
Integer         = Base(int, 'Integer')
Matrix          = Base(MatrixBase, 'Matrix')
OutputSystem    = Base(OutputBase, 'OutputSystem')
SetArray        = Base(set, 'SetArray')
StringArray     = Base(str, 'StringArray')
UniqueArray     = Base(UniqueBase, 'UniqueArray')

'''
ExtendedFunctionSet     = Base(FunctionBase)
FunctionalBuiltinSet    = Base(FunctionBase)

RawIntegerConstants         = Base(ConstantsBase)
RawStringConstants          = Base(ConstantsBase)
RawFloatingPointConstants   = Base(ConstantsBase)
'''

TYPES = [Array, Binary, Boolean, Complex, FloatingPoint, InputSystem, Integer,
             Matrix, OutputSystem, SetArray, StringArray, UniqueArray]

## Manual add

Array.add_method('Convert', convert('Array'), 1, verify = False)
Array.add_method('SortArrayByKeyFunction', lambda a, k: sorted(a, key = k), 2, verify = False)
Array.add_method('MapFunctionOverArray', lambda a, f: list(map(f, a)), 2, verify = False)
Array.add_method('ReduceArrayByDyad', lambda a, f: functools.reduce(f, a), 2, verify = False)
Array.add_method('ScanDyadOverArray', lambda a, f: list(itertools.accumulate(a, f)), 2, verify = False)
Array.add_method('ZipArraysWithIntermediateFunction', zipwith, 3, verify = False)
Array.add_method('MapSpreadFunctionOverArray', lambda a, f: list(itertools.starmap(f, a)), 2, verify = False)
Array.add_method('MapFunctionOverNeighbouringElements', lambda a, f: zipwith(a, a[1:], f), 2, verify = False)
Array.add_method('AppendElement', lambda a, b: a + [b], 2, verify = False)
Array.add_method('AppendElements', lambda a, *b: a + list(b), -1, verify = False)
Array.add_method('ExtractElementFromIndex', lambda a, b: a.pop(b), 2, verify = False)
Array.add_method('FindElementAtIndex', lambda a, b: a[b], 2, verify = False)
Array.add_method('FindIndexOfElement', lambda a, b: a.index(b), 2, verify = False)
Array.add_method('CountOccurencesOfElement', lambda a, b: a.count(b), 2, verify = False)
Array.add_method('ReverseArray', lambda a: list(reversed(a)), 1)
Array.add_method('SortArrayInAscendingOrder', sorted, 1)
Array.add_method('SortArrayInDescendingOrder', lambda a: sorted(a, reverse = True), 1)
Array.add_method('RebuildIntegerFromPrimeExponents', from_exponents, 1)
Array.add_method('FlattenAllSubarrays', flatten, 1)
Array.add_method('CountNumberOfElements', len, 1)
Array.add_method('CountFlattenedNumberOfElements', lambda a: len(flatten(a)), 1)
Array.add_method('Sum', lambda a: sum(a[1:], a[0]), 1)

Binary.add_method('Increment', lambda a: BinaryBase(a.from_binary() + 1), 1)
Binary.add_method('Decrement', lambda a: BinaryBase(a.from_binary() - 1), 1)
Binary.add_method('ConvertFromBinaryToInteger', lambda a: a.from_binary(), 1)
Binary.add_method('BinarySum', lambda a, b: BinaryBase(a.from_binary() + b.from_binary()), 2)
Binary.add_method('BinaryDifference', lambda a, b: BinaryBase(abs(a.from_binary() - b.from_binary())), 2)
Binary.add_method('BinaryProduct', lambda a, b: BinaryBase(a.from_binary() * b.from_binary()), 2)
Binary.add_method('BitwiseAnd', lambda a, b: BinaryBase(a.from_binary() & b.from_binary()), 2)
Binary.add_method('BitwiseOr', lambda a, b: BinaryBase(a.from_binary() | b.from_binary()), 2)
Binary.add_method('BitwiseXor', lambda a, b: BinaryBase(a.from_binary() ^ b.from_binary()), 2)
Binary.add_method('BitwiseNot', lambda a: ~a, 1)

Boolean.add_method('LogicalAnd', lambda a, b: a and b, 2)
Boolean.add_method('LogicalOr', lambda a, b: a or b, 2)
Boolean.add_method('LogicalNot', lambda a: not a, 1)
Boolean.add_method('LogicalXor', lambda a, b: (a or b) and not (a and b), 2)
Boolean.add_method('LogicalNand', lambda a, b: not (a and b), 2)
Boolean.add_method('LogicalNor', lambda a, b: not (a or b), 2)
Boolean.add_method('LogicalXnor', lambda a, b: not (a or b) and (a and b), 2)
Boolean.add_method('Equality', lambda a, b: a == b, 2)
Boolean.add_method('Inequality', lambda a, b: a != b, 2)

Complex.add_method('IncrementRealValue', lambda a: a + 1, 1)
Complex.add_method('DecrementRealValue', lambda a: a - 1, 1)
Complex.add_method('IncrementImaginaryValue', lambda a: a + 1j, 1)
Complex.add_method('DecrementImaginaryValue', lambda a: a - 1j, 1)
Complex.add_method('PhaseInRadians', cmath.phase, 1)
Complex.add_method('PhaseInDegrees', lambda a: math.degrees(cmath.phase(a)), 1)
Complex.add_method('PhaseAsMultiplierOfPi', lambda a: cmath.phase(a) / math.pi, 1)
Complex.add_method('Modulus', abs, 1)
Complex.add_method('ExpressInPolarCoordinateForm', cmath.polar, 1)
Complex.add_method('ExpressInRectangularCoordinateForm', cmath.rect, 1)
Complex.add_method('GaussianPrimality', gaussian_prime, 1)

InputSystem.add_method('ReadLineOfInput', InputBase.read_line, 1, verify = False, convert = False)
InputSystem.add_method('ReadEvaluatedLineOfInput', InputBase.read_eval, 1, verify = False, convert = False)
InputSystem.add_method('ReadCharacterOfInput', InputBase.read_char, 1, verify = False, convert = False)
InputSystem.add_method('ReadIntegerFromInput', InputBase.read_int, 1, verify = False, convert = False)
InputSystem.add_method('ExhaustRemainingInput', InputBase.read_rest, 1, verify = False, convert = False)
InputSystem.add_method('ReadCharacterOfInputAsInteger', InputBase.read_intchar, 1, verify = False, convert = False)
InputSystem.add_method('NewInput', new('input'), 1, verify = False, convert = False)
InputSystem.add_method('ReadCommandLineArgument', InputBase.read_argv, 1, verify = False, convert = False)

Integer.add_method('AbsoluteDifference', lambda a, b: abs(a - b), 2)
Integer.add_method('Primality', lambda a: is_prime(a), 1)
Integer.add_method('ConvertToListOfBaseDigits', to_base, 2)
Integer.add_method('ConvertToListOfBaseTenDigits', to_base, 1)
Integer.add_method('DecomposeIntoListOfPrimeFactors', prime_factors, 1)
Integer.add_method('DecomposeIntoListOfPrimeExponents', prime_exponents, 1)
Integer.add_method('ConvertToCharacter', chr, 1)
Integer.add_method('GreatestCommonDivisor', math.gcd, 2)

Matrix.add_method('Product', MatrixBase.mul, 2, verify = False)
Matrix.add_method('Determinant', MatrixBase.det, 1)
Matrix.add_method('Transpose', MatrixBase.transpose, 1)
Matrix.add_method('Reshape', MatrixBase.reshape, 3, verify = (MatrixBase, int, int))
Matrix.add_method('Sum', MatrixBase.add, 2)
Matrix.add_method('Difference', MatrixBase.sub, 2)
Matrix.add_method('Power', MatrixBase.pow, 2, verify = (MatrixBase, int))
Matrix.add_method('Negate', MatrixBase.neg, 1)
Matrix.add_method('Dimensions', lambda m: m.dims, 1)
Matrix.add_method('NumberOfElements', lambda m: m.rows * m.columns, 1)
Matrix.add_method('Adjugate', MatrixBase.adjugate, 1)
Matrix.add_method('Inverse', MatrixBase.inverse, 1)

OutputSystem.add_method('DisplayAsText', OutputBase.print, 2, verify = False, convert = False)
OutputSystem.add_method('ReturnDisplayedText', lambda s, a: OutputBase.print(s, a, ret = True), 2, verify = False, convert = False)
OutputSystem.add_method('DisplayWithSeparator', OutputBase.print, 3, verify = False, convert = False)
OutputSystem.add_method('DisplayWithTerminator', lambda s, a, b: OutputBase.print(s, a, end = b), 3, verify = False, convert = False)
OutputSystem.add_method('DisplayWithSeparatorAndTerminator', OutputBase.print, 4, verify = False, convert = False)
OutputSystem.add_method('DisplayIntegersAsCharacters', OutputBase.chr_print, 2, verify = False, convert = False)
OutputSystem.add_method('ActivateHoldBack', OutputBase.holdback, 1, verify = False, convert = False)
OutputSystem.add_method('FlushHoldBack', OutputBase.flush, 1, verify = False, convert = False)
OutputSystem.add_method('NewOutput', new('output'), 1, verify = False, convert = False)

SetArray.add_method('AddNewElement', set.add, 2, verify = False)
SetArray.add_method('RemoveExistingElement', set.remove, 2, verify = False)
SetArray.add_method('Intersection', set.intersection, 2)
SetArray.add_method('Union', set.union, 2)
SetArray.add_method('Difference', set.difference, 2)
SetArray.add_method('SymmetricalDifference', set.symmetric_difference, 2)
SetArray.add_method('RemovePossiblyExistingElement', set.discard, 2)
SetArray.add_method('CountNumberOfElements', len, 1)

StringArray.add_method('ConvertToOrdinals', lambda a: list(map(ord, a)), 1)
StringArray.add_method('ConvertToLowerCase', lambda a: a.lower(), 1)
StringArray.add_method('ConvertToUpperCase', lambda a: a.upper(), 1)
StringArray.add_method('CountNumberOfElements', len, 1)

UniqueArray.add_method('NewUniqueArray', new('unique'), 1, verify = False, convert = False)
UniqueArray.add_method('CountNumberOfElements', len, 1)

## Auto add

inc = lambda a: a + 1
dec = lambda a: a - 1

def sum_(*args):
    return sum(args)

data = zip(['Increment', 'Decrement', 'Sum', 'Difference', 'Product',
            'Quotient', 'Exponentiation', 'RemainderDivision', 'Negate'],
           [inc, dec, sum_, operator.sub, operator.mul, operator.floordiv, pow, operator.mod, operator.neg],
           [1, 1, -1, 2, 2, 2, 2, 2, 1])

for name, fun, arity in data:
    Integer.add_method(name, fun, arity)
    FloatingPoint.add_method(name, fun, arity)
    if name not in ['Increment', 'Decrement']:
        Complex.add_method(name, fun, arity)

for type_ in TYPES:
    type_.add_method('Convert', convert(type_.type_name), 1, verify = False, convert = False)
