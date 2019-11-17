import argparse
import re
import sys

import _exceptions as exceptions
import _parser as parser
import _types as types

global LINE, LINES

includes = {}
structures = {}
variables = {}

CONSTS = (
    'For', 'While', 'Do', 'Until', 'Each', 'If', 'IfNot',
)

STRUCTS = (
    'Loops', 'Conditionals',
)

class Loops:
    def __init__(self):
        self.loop_type = None
        
    def construct_loop(self, args, block):
        self.loop_type, *args = args
        switch = {
            'For':      self.for_loop,
            'While':    self.while_loop,
            'Do':       self.do_loop,
            'Until':    self.until_loop,
            'Each':     self.each_loop,
            'If':       self.if_statement,
            'IfNot':    self.ifnot_statement,
        }
        try:
            option = switch[self.loop_type]
        except KeyError:
            exceptions.ShowError('TypeError: Unknown looping type \'{}\''.format(self.loop_type), LINES, LINE)
        args = args + [block]
        option(*args)

    def for_loop(self, var, iters, block):
        self.loop_var = var
        for i in range(iters):
            variables[self.loop_var] = i + 1
            main(block, parse = False)

    def while_loop(self, var, block):
        self.loop_var = var
        while variables[self.loop_var]:
            main(block, parse = False)

    def do_loop(self, var, block):
        self.loop_var = var
        main(block, parse = False)
        while variables[self.loop_var]:
            main(block, parse = False)

    def until_loop(self, var, block):
        self.loop_var = var
        while not variables[self.loop_var]:
            main(block, parse = False)

    def each_loop(self, var, iterable, block):
        self.loop_var = var
        for elem in iterable:
            variables[self.loop_var] = elem
            main(block, parse = False)

    def if_statement(self, var, block):
        self.loop_var = var
        if variables[self.loop_var]:
            main(block, parse = False)

    def ifnot_statement(self, var, block):
        self.loop_var = var
        if not variables[self.loop_var]:
            main(block, parse = False)

def not_included(*options, mode = 0):
    '''
    mode = 0  :  Any are included
    mode = 1  :  All are included
    '''
    for option in options:
        if option in includes:
            return not mode
    return mode

def func_eval(cls_name, method_name, args, block):
    if block is None:
        cls = getattr(types, cls_name)
        args = list(map(evaluate, args))
        ret = cls.call_method(method_name, *args)

    else:
        if cls_name == 'Loops':
            cls = Loops()
            loop_type, loop_var, *args = args
            args = [loop_type, loop_var] + list(map(evaluate, args))
            cls.construct_loop(args, block)
            ret = None
        
    return ret

def iter_eval(array):
    array_type = 'array'
    if array[0] == '(':
        array_type = 'matrix'
    if array[0] == '{':
        array_type = 'set'

    if array_type == 'array':
        if not_included(types.Array):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as an array'.format(array), LINES, LINE)
            
        blank = []
        for elem in array:
            blank.append(evaluate(elem))
        return blank

    if array_type == 'set':
        if not_included(types.SetArray):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a set array'.format(array), LINES, LINE)
            
        blank = set()
        for elem in array[1:-1]:
            blank.add(evaluate(elem))
        return blank

    if array_type == 'matrix':
        if not_included(types.Matrix):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a matrix'.format(array), LINES, LINE)
            
        elements = list(filter(lambda a: a not in '()', array))
        counted = len(elements)
        width = array.count('(')
        blank = types.MatrixBase(width, counted // width)
        for elem in elements:
            blank.add_next(evaluate(elem))
        return blank

def evaluate(string, parse_check = True):
    if isinstance(string, parser.Iterable):
        return iter_eval(string.vals)

    if isinstance(string, parser.Bool):
        if not_included(types.Boolean):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a boolean'.format(array), LINES, LINE)
        return string.bool

    if isinstance(string, parser.Function):
        if string.method is string.args is string.block is None and string.cls in variables.keys():
            return variables[string.cls]
        return func_eval(string.cls, string.method, string.args, string.block)

    if string in variables.keys():
        return variables[string]

    if not isinstance(string, str):
        exceptions.ShowError('TypeError: Unexpected type \'{}\''.format(type(string)), LINES, LINE)

    if string[0] == '"' == string[-1]:
        return string[1:-1]

    if string[0] == 'b':
        if not_included(types.Binary):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a binary integer'.format(array), LINES, LINE)
        return types.BinaryBase(string[1:])
    
    if string[-1] == 'b':
        if not_included(types.Binary):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a binary integer'.format(string), LINES, LINE)
        return types.BinaryBase(int(string[:-1]))

    if string == '0':
        if not_included(types.Complex, types.FloatingPoint, types.Integer):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as 0'.format(string), LINES, LINE)
        return 0
    
    if re.search(r'^-?[1-9]\d*$', string):
        if not_included(types.Integer):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as an integer'.format(string), LINES, LINE)
        return int(string)
    
    if re.search(r'^-?([1-9]\d*|0)\.\d+$', string):
        if not_included(types.FloatingPoint):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a floating point number'.format(string), LINES, LINE)
        return float(string)
    
    if re.search(r'^-?([1-9]\d*|0)\.\d*\|\d+$', string):
        if not_included(types.FloatingPoint):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a floating point number'.format(string), LINES, LINE)
        return types.RecurringDecimal(*map(eval, string.split('|')))

    if re.search(r'^-?(([1-9]\d*|0)(\.\d+)?)[+-](([1-9]\d*|0)(\.\d+)?)[ij]$', string):
        if not_included(types.Complex):
            exceptions.ShowError('TypeError: Unable to interpret \'{}\' as a complex number'.format(string), LINES, LINE)
        return eval(string.replace('i', 'j'))

    if string in ['DEFAULT', 'ERROR']:
        return string

    parsed = parser.parser('PRIVATEVAR = ' + string)
    if (
        len(parsed) == 1 and
        isinstance(parsed[0], parser.Assignment) and
        parsed[0].var == 'PRIVATEVAR' and
        parse_check
    ):
        return evaluate(parsed[0].val, parse_check = False)
        
    exceptions.ShowError('SyntaxError: \'{}\''.format(string), LINES, LINE)

def main(code, parse = True):
    global LINE
    
    if parse:
        try:
            tokens = parser.parser(code)
        except exceptions.CustomException as e:
            print('Parsing Error:\n\t', e, sep = '', file = sys.stderr)
            sys.exit(1)
        except:
            print('Parsing Error', file = sys.stderr)
            sys.exit(1)
            
        lines = code.split('\n')
    else:
        tokens = code

    for tkn in tokens:
        if isinstance(tkn, parser.Assignment):
            if len(tkn.var) < 5:
                exceptions.ShowError('VariableNameLengthException: \'{}\' is under 5 characters'.format(tkn.var), LINES, LINE)
            try:
                    variables[tkn.var] = evaluate(tkn.val)
            except Exception as e:
                regex = re.compile(r"module '_types' has no attribute '(.*?)'")
                if regex.search(str(e)):
                    e = 'TypeError: Unknown type: \'{}\''.format(regex.findall(str(e))[0])
                exceptions.ShowError(e, LINES, LINE)
            LINE += 1
            
        elif isinstance(tkn, parser.Function):
            
            if tkn.method == 0:
                LINE += parse
                name = re.findall('(Include(?:Type|Structure)Package|TypeMethods)', tkn.cls)[0]
                arg = tkn.args[0]
                
                if name == 'IncludeTypePackage':
                    if hasattr(types, arg): includes[arg] = getattr(types, arg)
                    else: exceptions.ShowError('TypeError: Unknown type package: \'{}\''.format(arg), LINES, LINE)
                    
                if name == 'IncludeStructurePackage':
                    if arg in STRUCTS: structures[arg] = Loops
                    else: exceptions.ShowError('TypeError: Unknown structure package: \'{}\''.format(arg), LINES, LINE)
                    
                if name == 'TypeMethods':
                    if arg in includes.keys():
                        print(list(includes[arg].attrs.keys()), file = sys.stderr)
                    else:
                        exceptions.ShowError('TypeError: Unable to display methods of unknown type \'{}\''.format(arg), LINES, LINE)
                
            else:
                LINE += parse
                
                try:
                    func_eval(tkn.cls, tkn.method, tkn.args, tkn.block)
                except Exception as e:
                    print(e)
                    
                LINE += len(tkn.block or [])

        elif isinstance(tkn, parser.Blank):
            LINE += 1
            
        else:
            exceptions.ShowError('Syntax Error: Unknown token \'{}\''.format(tkn), LINES, LINE)
        
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog = './verbosity')

    getcode = argparser.add_mutually_exclusive_group()
    getcode.add_argument('-f', '--file', help = 'Read code from a file', action = 'store_true')
    getcode.add_argument('-c', '--cmd', '--cmdline', help = 'Read code from command line', action = 'store_true')

    argparser.add_argument('program')
    argparser.add_argument('input', nargs = '*', type = evaluate)
    settings = argparser.parse_args()

    if settings.file:
        filename = settings.program
        with open(filename) as file:
            code = file.read()

    elif settings.cmd:
        code = settings.program

    variables['ARGV'] = settings.input
    for i, argv in enumerate(settings.input):
        variables['ARGV{}'.format(i)] = argv

    LINE = 1
    LINES = code.split('\n')
    main(code)
    sys.exit(0)
