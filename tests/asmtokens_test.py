from __future__ import print_function
import sys
import ply.lex as lex
import asm2d.asmtokens as asmtokens

def test_lexer(input_string):
    asmlexer = lex.lex(module=asmtokens)
    asmlexer.errors = False
    asmlexer.input(input_string)

    result = []
    while True:
        token = asmlexer.token()
        if not token: break
        result = result + [(token.type, token.value)]

    if asmlexer.errors:
        sys.exit(1)

    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: asmtokens_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    result = test_lexer(contents)

    for pair in result:
        print(pair)

if __name__ == '__main__':
    main()
