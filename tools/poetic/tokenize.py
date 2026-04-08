import argparse, re, sys

def tokenize_file(path, wimpmode=False):
    with open(path, encoding="utf8") as f:
        data = f.read()
    if wimpmode:
        program = "".join([c for c in data if c.isdigit()])
    else:
        program = "".join([c if c.isalpha() else ("" if c=="'" else " ") for c in data])
        program = "".join([str(len(w)) if len(w)!=10 else "0" for w in program.split()])
    tokens = re.findall(r"((?:[3456]\d)|\d)", program)
    return tokens

def main():
    parser = argparse.ArgumentParser(description='Tokenize a Poetic program (same rules as poetic.py)')
    parser.add_argument('program', help='file to tokenize')
    parser.add_argument('-w', '--wimpmode', action='store_true', help='wimpmode: keep only digits')
    args = parser.parse_args()
    try:
        tokens = tokenize_file(args.program, args.wimpmode)
    except FileNotFoundError:
        print('File not found:', args.program, file=sys.stderr)
        sys.exit(2)
    print('TOKENS:', tokens)

if __name__ == '__main__':
    main()
