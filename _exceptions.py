import sys

class CustomException(Exception):
        def __init__(self, name):
                self.name = name
        def __repr__(self):
                return 'Exception:{}'.format(self.name)

def RaiseException(name):
        raise CustomException(name)

def ShowError(exp, line, number):
        if type(exp) != CustomException:
                ShowError(CustomException('UnknownErrorThrown: {}'.format(exp)), line, number)
        if repr(exp) == 'Exception:InvalidSyntax':
                msg = '''InvalidSyntax in the code:

{}

Excecution terminated'''
                formats = [line]
        else:
                msg = '''In line {}:
    {} thrown by:
        '{}'

Excecution terminated'''
                formats = [number, repr(exp), line]

        print(msg.format(*formats), file=sys.stderr)
        sys.exit()
