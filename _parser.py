import re

import _exceptions as exceptions

num_regex = r'^(-?(([1-9]\d*|0)(\.\d+(\|\d+)?)?)([+-](([1-9]\d*|0)(\.\d+(\|\d+)?)?)?[ij])?)|(b[10]+)|([10]+b)$'

class Function:
    def __init__(self, cls):
        self.cls = cls
        self.method = None
        self.args = None
        self.arity = 0
        self.block = None

    def add_method(self, method):
        self.method = method

    def add_args(self, *args):
        if self.args is None:
            self.args = []
            
        for arg in args:
            self.args.append(arg)
            self.arity += 1

    def add_block(self, block):
        if self.block is None:
            self.block = ''
        self.block += block
        pass

    def __repr__(self):
        if self.args is not None:
            disp = '; '.join(map(str, self.args))
            
            if self.block is None:
                if self.method == 0:
                    
                    return '{}<{}>'.format(self.cls, disp)
                return '{}:{}<{}>'.format(self.cls, self.method, disp)
            return '{}:{}<{}> {}'.format(self.cls, self.method, disp, self.block)

        if self.method == 0:
            return '{}<...>'.format(self.cls)

        if self.method is not None:
            return '{}:{}<...>'.format(self.cls, self.method)

        return '{}:[...]<...>'.format(self.cls)

    def __str__(self):
        return repr(self)

class Assignment(Function):
    def __init__(self, var):
        self.var = var
        self.val = None

    def assign(self, val):
        self.val = val

    def __repr__(self):
        if self.val is None:
            return '{} = ...'.format(self.var)
        return '{} = {}'.format(self.var, self.val)

    def __str__(self):
        return repr(self)

class Iterable:
    def __init__(self):
        self.type = None
        self.vals = []

    def __repr__(self):
        out = '('
        for elem in self.vals:
            if elem in '(){}':
                out = out.strip() + elem
            else:
                out += elem + ' '
        return out + ')'

    def add_val(self, val):
        self.vals.append(val)

    def to_list(self):
        self.type = 'list'

    def to_mat(self):
        self.type = 'mat'

class Bool:
    def __init__(self, value):
        self.bool = (value == 'true')

    def __repr__(self):
        return 'true' if self.bool else 'false'

def parser(string):
    tokens = []
    token = None
    tkns = re.findall(r'[A-Za-z]+|\d+|.|\n', string + '\n')
    tkns = iter(tkns)
    
    func = False
    cls = False
    arg = False
    str_ = False
    assign = False
    block = False
    comment = False
    iterable = 0

    string_arg = ''
    
    for tkn in tkns:

        if comment and tkn != '\n':
            continue

        if tkn == '-':
            tkn = '-' + next(tkns)
            
        if str_ and tkn != '"':
            string_arg += tkn

        elif iterable and tkn not in '( )':
            tokens[-1].add_val(tkn)

        elif block and tkn != ']':
            tokens[-1].add_block(tkn)
            
        elif re.search(r'[A-Za-z]+|\d+', tkn):
            if assign:
                value = ''
                while tkn != '\n':
                    value += tkn
                    tkn = next(tkns)

                if re.search(num_regex, value):
                    tokens[-1].assign(value)
                elif value in ['true', 'false']:
                    tokens[-1].assign(Bool(value))
                else:
                    tokens[-1].assign(parser(value)[0])
                    
                assign = False
                continue
            
            if not cls:
                tokens.append(Function(tkn))
                if re.search(r'Include(Type|Structure)Package|TypeMethods', tkn):
                    tokens[-1].add_method(0)
                    cls = True
                continue

            if not func:
                tokens[-1].add_method(tkn)
                continue

            if not arg:
                tokens[-1].add_args(tkn)
                arg = True
                continue

            exceptions.RaiseException('SpareTokenException: \'{}\''.format(tkn))

        elif tkn == '"':
            str_ = not str_
            if not str_ and not arg:
                if isinstance(tokens[-1], Assignment):
                    tokens[-1].assign(string_arg.join('""'))
                else:
                    tokens[-1].add_args(string_arg.join('""'))
                string_arg = ''

        elif tkn == ';':
            arg = False

        elif tkn == ':':
            cls = True

        elif tkn == '<':
            func = True

        elif tkn == '>':
            arg = True

        elif tkn == '[':
            block = True

        elif tkn == '#':
            comment = True

        elif tkn == ']' and block:
            tokens[-1].block = parser(tokens[-1].block)
            block = False

        elif tkn == '=':
            tokens.append(Assignment(tokens.pop().cls))
            assign = True

        elif tkn == '(':
            if iterable:
                iterable += 1
                tokens[-1].add_val(tkn)
            else:
                tokens.append(Iterable())
                iterable = 1

        elif tkn == ')':
            iterable -= 1
            if iterable == 0:
                val = tokens.pop()
                if isinstance(tokens[-1], Assignment):
                    tokens[-1].assign(val)
                else:
                    tokens[-1].add_args(val)
            else:
                tokens[-1].add_val(tkn)

        elif tkn == '\n':
            func = cls = arg = assign = comment = False

        elif re.search(r'[ \t]+', tkn):
            continue

        else:
            exceptions.RaiseException('SyntaxError: \'{}\''.format(tkn))

    return tokens
