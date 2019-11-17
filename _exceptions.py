import sys

class CustomException(Exception):
        def __init__(self, name):
                self.name = name
        def __repr__(self):
                return 'Exception:{}'.format(self.name)

def RaiseException(name):
        raise CustomException(name)

def ShowError(exp, lines, number):
        line = lines[number - 1]
        msg = '''{}
    thrown in line {}:
        '{}'

Excecution terminated'''
        formats = [exp, number, line]

        print(msg.format(*formats), file=sys.stderr)
        sys.exit(1)
