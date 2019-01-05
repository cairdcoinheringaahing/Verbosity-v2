import sys

import _exceptions as exceptions
import _parser as parser
import _types as types

def main(code, *argv):
    pass

if __name__ == '__main__':
    tests = ['hw', 'example']
    for filename in tests:
        file = open(filename, 'r', encoding = 'utf-8')
        content = file.read()
        file.close()

        main(content)
        print()
