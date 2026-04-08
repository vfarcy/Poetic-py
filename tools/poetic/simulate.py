import argparse
import re
import sys
import time


def tokenize_text(data, wimpmode=False):
    if wimpmode:
        program = "".join([c for c in data if c.isdigit()])
    else:
        program = "".join([c if c.isalpha() else ("" if c=="'" else " ") for c in data])
        program = "".join([str(len(w)) if len(w)!=10 else "0" for w in program.split()])
    tokens = re.findall(r"((?:[3456]\d)|\d)", program)
    return tokens


def load_tokens_from_file(path, wimpmode=False):
    try:
        with open(path, encoding="utf8") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)
    return tokenize_text(data, wimpmode=wimpmode)


def dump_state(step, ip, token, instr, arg, mp, val, memory, window=8):
    INSTR_NAMES = {
        '0': 'END', '1': 'IF', '2': 'EIF', '3': 'INC', '4': 'DEC',
        '5': 'FWD', '6': 'BAK', '7': 'OUT', '8': 'IN', '9': 'RND'
    }
    inst_name = INSTR_NAMES.get(instr, 'UNK')
    mem_slice = list(memory[mp:mp+window])
    print(f"S{step:04d} IP={ip:04d} TOK={token!r} INST={instr}({inst_name}) ARG={arg} MP={mp} VAL={val} MEM[{mp}:{mp+window}]={mem_slice}")


def simulate(tokens, step_mode=False, max_steps=10000, delay=0.0):
    instructionPointer = 0
    memory = bytearray(30000)
    memoryPointer = 0
    eofReached = False
    step = 0

    while True:
        if max_steps is not None and step >= max_steps:
            print(f"Reached max steps ({max_steps}). Stopping.")
            break
        try:
            token = tokens[instructionPointer]
            currentInstruction = token[0]
        except Exception:
            print("ERROR: Unexpected EOF during simulation")
            break

        currentArgument = None
        try:
            currentArgument = int(token[1])
            if currentArgument == 0:
                currentArgument = 10
        except Exception:
            pass

        # dump current state
        dump_state(step, instructionPointer, token, currentInstruction, currentArgument, memoryPointer, memory[memoryPointer], memory)

        # execute instruction
        if currentInstruction == "0":
            print("END encountered. Simulation finished.")
            break
        elif currentInstruction == "1":
            if memory[memoryPointer] == 0:
                nested = 1
                while nested:
                    instructionPointer += 1
                    try:
                        if tokens[instructionPointer][0] == "1":
                            nested += 1
                        elif tokens[instructionPointer][0] == "2":
                            nested -= 1
                    except Exception:
                        print("ERROR: Mismatched IF/EIF during simulation")
                        return
            else:
                instructionPointer += 1
        elif currentInstruction == "2":
            if memory[memoryPointer] != 0:
                nested = -1
                while nested:
                    instructionPointer -= 1
                    try:
                        if tokens[instructionPointer][0] == "1":
                            nested += 1
                        elif tokens[instructionPointer][0] == "2":
                            nested -= 1
                    except Exception:
                        print("ERROR: Mismatched IF/EIF during simulation")
                        return
            else:
                instructionPointer += 1
        elif currentInstruction == "3":
            if currentArgument is None:
                print("ERROR: Missing argument for INC")
                return
            memory[memoryPointer] = (memory[memoryPointer] + currentArgument) % 256
            instructionPointer += 1
        elif currentInstruction == "4":
            if currentArgument is None:
                print("ERROR: Missing argument for DEC")
                return
            memory[memoryPointer] = (memory[memoryPointer] - currentArgument) % 256
            instructionPointer += 1
        elif currentInstruction == "5":
            if currentArgument is None:
                print("ERROR: Missing argument for FWD")
                return
            memoryPointer = (memoryPointer + currentArgument) % len(memory)
            instructionPointer += 1
        elif currentInstruction == "6":
            if currentArgument is None:
                print("ERROR: Missing argument for BAK")
                return
            memoryPointer = (memoryPointer - currentArgument) % len(memory)
            instructionPointer += 1
        elif currentInstruction == "7":
            # OUT
            sys.stdout.write(chr(memory[memoryPointer]))
            sys.stdout.flush()
            instructionPointer += 1
        elif currentInstruction == "8":
            # IN - simulation will not read from stdin; mark EOF
            if eofReached:
                pass
            else:
                eofReached = True
            instructionPointer += 1
        elif currentInstruction == "9":
            import random
            memory[memoryPointer] = random.randint(0,255)
            instructionPointer += 1
        else:
            print(f"ERROR: Unknown instruction {currentInstruction}")
            return

        step += 1
        if step_mode:
            try:
                input("Press Enter to continue (or Ctrl-C to stop)...")
            except KeyboardInterrupt:
                print("Stopped by user")
                break
        else:
            if delay > 0:
                time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Tokenize and simulate Poetic programs (step-by-step)")
    parser.add_argument('program', help='file to run or tokenize')
    parser.add_argument('-w', '--wimpmode', action='store_true', help='wimpmode: keep only digits')
    parser.add_argument('--tokens', action='store_true', help='print tokens and exit')
    parser.add_argument('--simulate', action='store_true', help='simulate execution (prints trace)')
    parser.add_argument('--step', action='store_true', help='step mode: wait for Enter between instructions')
    parser.add_argument('--max-steps', type=int, default=10000, help='max steps to execute')
    parser.add_argument('--delay', type=float, default=0.0, help='delay between steps when not stepping (seconds)')
    args = parser.parse_args()

    tokens = load_tokens_from_file(args.program, wimpmode=args.wimpmode)
    if args.tokens:
        print('TOKENS:', tokens)
        return

    if args.simulate:
        simulate(tokens, step_mode=args.step, max_steps=args.max_steps, delay=args.delay)
    else:
        print('No action requested. Use --tokens or --simulate')


if __name__ == '__main__':
    main()
