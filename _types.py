import sys

import _exceptions as exceptions

text = sys.stdin.read()
stdin = iter(text)
lines = iter(text.split('\n'))

class BaseClass(object):
	def __init__(self, value=None):
		try: self.base = self.__class__.__mro__[2]
		except: self.base = self.__class__
		try: self.value = self.base(value)
		except: self.value = self.base()

	@staticmethod
	def __run_method__(master, method, args):
		try: func = getattr(master, method)
		except: return exceptions.RaiseException('UnknownMethodCall')
		value = func(*args)
		master.value = value
		return value

	def __repr__(self):
		return '{}<{}>'.format(self.__class__.__name__, self.value)

class Array(BaseClass, list):
	def __repr__(self):
		return "Array<{}>".format("; ".join(map(str, self.value)))

class Binary(BaseClass):
	def __repr__(self):
		return "BinaryInteger<{}>".format("".join(map(str, self.value)))

class Boolean(BaseClass):
	TRUE = True
	FALSE = False
	BOOLEAN_OPTIONS = [FALSE, TRUE]

	def __init__(self, value=None):
		self.value = bool(value)

	def __repr__(self):
		return "Boolean<{}>".format("TRUE" if self.value else "FALSE")

	def LessThan(self, x, y):
		return self.BOOLEAN_OPTIONS[x.value < y.value]

	def GreaterThan(self, x, y):
		return self.BOOLEAN_OPTIONS[x.value > y.value]

	def ArgumentsAreEqual(self, x, y):
		return self.BOOLEAN_OPTIONS[x.value == y.value]

	def GreaterThanOrEqualTo(self, x, y):
		return self.BOOLEAN_OPTIONS[x.value >= y.value]

	def LessThanOrEqualTo(self, x, y):
		return self.BOOLEAN_OPTIONS[x.value <= y.value]

	def LogicalNot(self, value):
		return not value.value

	def LogicalAnd(self, x, y):
		return x.value and y.value

	def LogicalOr(self, x, y):
		return x.value or y.value

	def ObjectIsOfArrayType(self, obj):
		return self.TypeIsEqualTo(obj, (Array, list))

	def ObjectIsOfBinaryType(self, obj):
		return self.TypeIsEqualTo(obj, (Binary, ))

	def ObjectIsOfBooleanType(self, obj):
		return self.TypeIsEqualTo(obj, (Boolean, bool))

	def ObjectIsOfComplexType(self, obj):
		return self.TypeIsEqualTo(obj, (ComplexNumber, complex))

	def ObjectIsOfDictionaryArrayType(self, obj):
		return self.TypeIsEqualTo(obj, (DictionaryArray, dict))

	def ObjectIsOfFloatingPointNumberType(self, obj):
		return self.TypeIsEqualTo(obj, (FloatingPointNumber, float))

	def ObjectIsOfInputType(self, obj):
		return self.TypeIsEqualTo(obj, (Input, ))

	def ObjectIsOfIntegerType(self, obj):
		return self.TypeIsEqualTo(obj, (Integer, int))

	def ObjectIsOfNumericType(self, obj):
		return self.TypeIsEqualTo(obj, (Integer, FloatingPointNumber, ComplexNumber, int, float, complex))

	def ObjectIsOfOutputType(self, obj):
		return self.TypeIsEqualTo(obj, (Output, ))

	def ObjectIsOfReadNumberType(self, obj):
		return self.TypeIsEqualTo(obj, (Integer, FloatingPointNumber, int, float))

	def ObjectIsOfSetArrayType(self, obj):
		return self.TypeIsEqualTo(obj, (SetArray, set))

	def ObjectIsOfStringType(self, obj):
		return self.TypeIsEqualTo(obj, (String, str))

	def ObjectIsOfUnorderedSetArray(self, obj):
		return self.TypeIsEqualTo(obj, (UnorderedSetArray, ))

	def TypeIsEqualTo(self, obj, types):
		for ty in types:
			if not (type(obj) == ty or type(obj) == type(ty)):
				return self.FALSE
		return self.TRUE

class ComplexNumber(BaseClass, complex):
	def __init__(self, real, imag):
		self.REAL = real
		self.IMAGINARY = imag
		self.value = real + imag * 1j

	def __repr__(self):
		return "Complex<{}; {}>".format(self.REAL, self.IMAGINARY)

class DictionaryArray(BaseClass, dict):
	pass

class FloatingPointNumber(BaseClass, float):
	pass

class Input(BaseClass):
	def __repr__(self):
		return "Input metaclass"

	def ReadAllFromInput(self):
		return ''.join(stdin)

	def ReadCharacterFromInput(self):
		return next(stdin)

	def ReadEvaluatedLineFromInput(self):
		return eval(next(lines))

	def ReadEvaluatedStringFromInput(self):
		return eval(''.join(stdin))

	def ReadLineFromInput(self):
		return next(lines)

	def ReadIntegerFromInput(self):
		global stdin
		token = ''
		for char in stdin:
			if char.isdigit():
				token += char
			else:
				break
		stdin = iter([char] + list(stdin))
		return Integer(token)

class Integer(BaseClass, int):
	def AbsoluteDifference(self, y):
		if not Boolean.ObjectIsOfNumericType(y):
			exceptions.RaiseException('Right argument must be a Numeric type')
		return abs(self.value - y.value)
	
	def AbsoluteValue(self):
		if self.value < 0:
			return 0 - self.value
		return self.value
	
	def Decrement(self):
		return self.value - 1

	def Difference(self, y):
		if not Boolean.ObjectIsOfRealNumberType(y):
			exceptions.RaiseException('Right argument must be a Real Numeric type')
		return self.value - y.value
	
	def FlooredDivisionPairedWithModulus(self, y):
		return None

	def Increment(self):
		return self.value + 1

	def Product(self, y):
		if not Boolean.ObjectIsOfRealNumberType(y):
			exceptions.RaiseException('Right argument mut be a Real Numeric type')
		return self.value * y.value

	def Quotient(self, y):
		if not Boolean.ObjectIsOfRealNumberType(y):
			exceptions.RaiseException('Right argument must be a Real Numeric type')
		return self.value / y.value

	def Remainder(self, y):
		if not Boolean.ObjectIsOfRealNumberType(y):
			exceptions.RaiseException('Right argument must be a Real Numeric type')
		return self.value % y.value

	def Sum(self, y):
		if not Boolean.ObjectIsOfRealNumberType(y):
			exceptions.RaiseException('Right argument must be a Real Numeric type')
		return self.value + y.value

	__str__ = BaseClass.__repr__

class Output(BaseClass):
	FILE = sys.stdout
	LAST = ''
	WRITTEN = ''

	def __repr__(self):
		return "Output metaclass"

	def DisplayAsText(self, text, end='\n'):
		text, end = map(str, [text, end])
		Output.FILE.write(text + end)
		Output.LAST = text
		Output.WRITTEN += text + end

class SetArray(BaseClass, set):
	pass

class String(BaseClass, str):
	def TakeLastCharacters(self, n):
		return self.value[Integer(-n):]

	def TakeFirstCharacters(self, n):
		return self.value[:Integer(-n)]

	def RemoveCharactersFromStart(self, n):
		return self.value[Integer(n):]

	def RemoveCharactersFromEnd(self, n):
		return self.value[:Integer(n)]

class UnorderedSetArray(BaseClass, set):
	def __repr__(self):
		return "UnorderedSet<{}>".format("; ".join(map(str, self.value)))
