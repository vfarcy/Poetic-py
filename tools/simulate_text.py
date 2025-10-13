#!/usr/bin/env python3
"""Simulate Poetic from direct text or file input.

Usage examples:
  python tools\simulate_text.py --text "bonjour le monde" --simulate
  python tools\simulate_text.py --text "une phrase" --tokens
  python tools\simulate_text.py examples\print_A.ptc -w --simulate
"""
import argparse
import re
import sys
import time
import random

MEMORY_SIZE = 30000


def tokenize_from_text(text: str, wimpmode: bool):
    if wimpmode:
        program = "".join(ch for ch in text if ch.isdigit())
        tokens = re.findall(r"((?:[3456]\d)|\d)", program)
        return tokens

    # Normal mode: convert words to lengths (10 -> '0')
    # remove apostrophes
    s = text.replace("'", "")
    # Replace non-letter characters by spaces. Include common Latin accented range to preserve French letters.
    s = re.sub(r"[^\w\u00C0-\u017F]+", " ", s, flags=re.UNICODE)
    # Keep words that contain at least one alphabetic character
    words = [w for w in s.split() if any(c.isalpha() for c in w)]
    lengths = ["0" if len(w) == 10 else str(len(w)) for w in words]
    program = "".join(lengths)
    tokens = re.findall(r"((?:[3456]\d)|\d)", program)
    return tokens


def simulate_tokens(tokens, step=False, delay=0.0, show_trace=False):
    memory = bytearray(MEMORY_SIZE)
    ptr = 0
    ip = 0
    eofReached = False
    output_chars = []

    def error(msg):
        print(f"ERROR: {msg}", file=sys.stderr)
        return False, "".join(output_chars)

    while ip < len(tokens):
        tok = tokens[ip]
        instr = tok[0]
        arg = None
        if len(tok) > 1:
            try:
                arg = int(tok[1])
            except ValueError:
                return error(f"Invalid argument in token '{tok}' at ip={ip}")
            if arg == 0:
                arg = 10

        if show_trace:
            INSTR_NAMES = {
                '0': 'END', '1': 'IF', '2': 'EIF', '3': 'INC', '4': 'DEC',
                '5': 'FWD', '6': 'BAK', '7': 'OUT', '8': 'IN', '9': 'RND'
            }
            inst_name = INSTR_NAMES.get(instr, 'UNK')
            mem_window = " ".join(str(b) for b in memory[ptr:ptr+10])
            print(f"IP={ip:03} TOK={tok:>2} INSTR={instr}({inst_name}) ARG={arg} PTR={ptr} MEM=[{mem_window}]")

        if instr == "0":
            # END
            break
        elif instr == "1":
            # IF: if current cell == 0, jump forward to matching EIF (2)
            if memory[ptr] == 0:
                depth = 1
                j = ip + 1
                while j < len(tokens) and depth > 0:
                    t = tokens[j][0]
                    if t == "1":
                        depth += 1
                    elif t == "2":
                        depth -= 1
                    j += 1
                if depth != 0:
                    return error("Mismatched IF/EIF (forward search)")
                ip = j
                if step:
                    input("press Enter to continue...")
                if delay and not step:
                    time.sleep(delay)
                continue
        elif instr == "2":
            # EIF: if current cell != 0, jump back to matching IF
            if memory[ptr] != 0:
                depth = 1
                j = ip - 1
                while j >= 0 and depth > 0:
                    t = tokens[j][0]
                    if t == "2":
                        depth += 1
                    elif t == "1":
                        depth -= 1
                    j -= 1
                if depth != 0:
                    return error("Mismatched IF/EIF (backward search)")
                ip = j + 1
                if step:
                    input("press Enter to continue...")
                if delay and not step:
                    time.sleep(delay)
                continue
        elif instr == "3":
            if arg is None:
                return error("Missing argument for INC (3)")
            memory[ptr] = (memory[ptr] + arg) % 256
        elif instr == "4":
            if arg is None:
                return error("Missing argument for DEC (4)")
            memory[ptr] = (memory[ptr] - arg) % 256
        elif instr == "5":
            if arg is None:
                return error("Missing argument for FWD (5)")
            ptr = (ptr + arg) % MEMORY_SIZE
        elif instr == "6":
            if arg is None:
                return error("Missing argument for BAK (6)")
            ptr = (ptr - arg) % MEMORY_SIZE
        elif instr == "7":
            ch = chr(memory[ptr])
            print(ch, end="", flush=True)
            output_chars.append(ch)
        elif instr == "8":
            # IN — during simulation we do not block: mark EOF and skip write
            eofReached = True
        elif instr == "9":
            memory[ptr] = random.randint(0, 255)
        else:
            return error(f"Unknown instruction '{instr}' at ip={ip}")

        ip += 1

        if step:
            input("press Enter to continue...")
        if delay and not step:
            time.sleep(delay)

    return True, "".join(output_chars)


def main():
    parser = argparse.ArgumentParser(description="Simulate Poetic tokens from text or file (supports --text).")
    parser.add_argument("-w", "--wimpmode", action="store_true", help="keep only digits from input (wimpmode)")
    parser.add_argument("-t", "--text", type=str, help="provide the source directly as text")
    parser.add_argument("--tokens", action="store_true", help="just print tokens and exit")
    parser.add_argument("--simulate", action="store_true", help="run simulation and show execution")
    parser.add_argument("--step", action="store_true", help="step mode (wait between instructions)")
    parser.add_argument("--delay", type=float, default=0.0, help="delay in seconds between steps when not stepping interactively")
    parser.add_argument("file", nargs="?", help="optional path to a .ptc file to read instead of --text")
    args = parser.parse_args()

    if args.text is None and args.file is None:
        print("Provide --text 'your text' or a file path", file=sys.stderr)
        sys.exit(1)

    if args.text is not None:
        source = args.text
    else:
        try:
            with open(args.file, "r", encoding="utf8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)

    tokens = tokenize_from_text(source, args.wimpmode)

    if args.tokens:
        print("TOKENS:", tokens)
        return

    if args.simulate:
        ok, out = simulate_tokens(tokens, step=args.step, delay=args.delay, show_trace=True)
        if not ok:
            sys.exit(1)
        if out and not out.endswith("\n"):
            print()
        return

    # default: print tokens and a short simulation summary (no trace)
    print("TOKENS:", tokens)
    ok, out = simulate_tokens(tokens, step=False, delay=0.0, show_trace=False)
    if not ok:
        sys.exit(1)
    if out and not out.endswith("\n"):
        print()


if __name__ == "__main__":
    main()
