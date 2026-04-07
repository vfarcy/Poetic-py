import random
import re
import time


class PoeticRuntimeError(Exception):
    pass


def tokenize_from_text(text, wimpmode=False):
    if wimpmode:
        program = "".join(ch for ch in text if ch.isdigit())
        return re.findall(r"((?:[3456]\d)|\d)", program)

    cleaned = "".join(ch if ch.isalpha() else ("" if ch == "'" else " ") for ch in text)
    lengths = ["0" if len(word) == 10 else str(len(word)) for word in cleaned.split()]
    program = "".join(lengths)
    return re.findall(r"((?:[3456]\d)|\d)", program)


def run_poetic(source, input_text="", wimpmode=False, max_steps=500000, max_output=100000, time_limit_s=2.0):
    tokens = tokenize_from_text(source, wimpmode=wimpmode)

    ip = 0
    memory = bytearray(30000)
    mp = 0
    input_pos = 0
    eof_reached = False
    output_chars = []

    start = time.time()
    steps = 0

    while True:
        if steps >= max_steps:
            raise PoeticRuntimeError("Execution stopped: max steps exceeded")
        if (time.time() - start) > time_limit_s:
            raise PoeticRuntimeError("Execution stopped: time limit exceeded")

        try:
            token = tokens[ip]
        except Exception:
            raise PoeticRuntimeError("Unexpected EOF")

        instr = token[0]
        arg = None
        if len(token) > 1:
            arg = int(token[1])
            if arg == 0:
                arg = 10

        if instr == "0":
            break
        elif instr == "1":
            if memory[mp] == 0:
                nested = 1
                while nested:
                    ip += 1
                    try:
                        if tokens[ip][0] == "1":
                            nested += 1
                        elif tokens[ip][0] == "2":
                            nested -= 1
                    except Exception:
                        raise PoeticRuntimeError("Mismatched IF/EIF")
            else:
                ip += 1
        elif instr == "2":
            if memory[mp] != 0:
                nested = -1
                while nested:
                    ip -= 1
                    try:
                        if tokens[ip][0] == "1":
                            nested += 1
                        elif tokens[ip][0] == "2":
                            nested -= 1
                    except Exception:
                        raise PoeticRuntimeError("Mismatched IF/EIF")
            else:
                ip += 1
        elif instr == "3":
            if arg is None:
                raise PoeticRuntimeError("Missing argument for INC")
            memory[mp] = (memory[mp] + arg) % 256
            ip += 1
        elif instr == "4":
            if arg is None:
                raise PoeticRuntimeError("Missing argument for DEC")
            memory[mp] = (memory[mp] - arg) % 256
            ip += 1
        elif instr == "5":
            if arg is None:
                raise PoeticRuntimeError("Missing argument for FWD")
            mp = (mp + arg) % len(memory)
            ip += 1
        elif instr == "6":
            if arg is None:
                raise PoeticRuntimeError("Missing argument for BAK")
            mp = (mp - arg) % len(memory)
            ip += 1
        elif instr == "7":
            output_chars.append(chr(memory[mp]))
            if len(output_chars) > max_output:
                raise PoeticRuntimeError("Execution stopped: output limit exceeded")
            ip += 1
        elif instr == "8":
            if eof_reached:
                pass
            else:
                if input_pos >= len(input_text):
                    eof_reached = True
                else:
                    ch = ord(input_text[input_pos]) % 256
                    input_pos += 1
                    if ch == 26:
                        eof_reached = True
                    else:
                        memory[mp] = ch
            ip += 1
        elif instr == "9":
            memory[mp] = random.randint(0, 255)
            ip += 1
        else:
            raise PoeticRuntimeError(f"Unknown instruction: {instr}")

        steps += 1

    return {
        "output": "".join(output_chars),
        "steps": steps,
        "tokens": len(tokens),
    }
