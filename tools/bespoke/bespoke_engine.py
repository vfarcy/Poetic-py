"""
Self-contained Bespoke language interpreter engine.

Language specification:
  https://github.com/WinslowJosiah/bespokelang/wiki/Documentation

Bespoke is a stack-based esolang that encodes instructions in word lengths,
similar to Poetic, but with arbitrary-precision integers, a heap, functions,
and structured control flow.
"""

import time
import unicodedata
from io import StringIO


# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------

class BespokeRuntimeError(Exception):
    pass


# ---------------------------------------------------------------------------
# Internal control-flow signals (not exposed to callers)
# ---------------------------------------------------------------------------

class _BreakSignal(Exception):
    pass

class _ReturnSignal(Exception):
    pass

class _EndProgramSignal(Exception):
    pass


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------

class _Token:
    __slots__ = ("cat", "cmd", "args")

    def __init__(self, cat, cmd="", args=()):
        self.cat = cat
        self.cmd = cmd
        self.args = tuple(args)

    def __repr__(self):
        return f"Token({self.cat!r},{self.cmd!r},{self.args!r})"


# ---------------------------------------------------------------------------
# Step 1 – text → digit string
# ---------------------------------------------------------------------------

def convert_to_digits(text: str) -> str:
    """Encode each word's letter count as digits (same rule as Poetic)."""
    normalized = unicodedata.normalize("NFKC", text)
    result = []
    word_letters = 0
    in_word = False

    for ch in normalized:
        is_letter = ch.isalpha()
        is_apos = ch in ("'", "\u2019")
        if is_letter or is_apos:
            if is_letter:
                word_letters += 1
            in_word = True
        else:
            if in_word and word_letters > 0:
                s = "0" if word_letters == 10 else str(word_letters)
                result.append(s)
            word_letters = 0
            in_word = False

    if in_word and word_letters > 0:
        s = "0" if word_letters == 10 else str(word_letters)
        result.append(s)

    return "".join(result)


# ---------------------------------------------------------------------------
# Step 2 – digit string → token list
# ---------------------------------------------------------------------------

def _tokenize(digits: str) -> list:
    tokens = []
    i = 0
    n = len(digits)

    def parse_sized_number():
        nonlocal i
        if i >= n:
            raise BespokeRuntimeError("Expected size digit, got end of program")
        size = int(digits[i]) or 10
        i += 1
        if i + size > n:
            raise BespokeRuntimeError("Incomplete number literal")
        num = digits[i:i + size]
        i += size
        return num

    while i < n:
        d = digits[i]
        i += 1

        if d in "124568":
            if i >= n:
                raise BespokeRuntimeError(f"Expected specifier after '{d}'")
            cmd = digits[i]; i += 1
            tokens.append(_Token(d, cmd))

        elif d == "7":
            if i >= n:
                raise BespokeRuntimeError("Expected specifier after '7'")
            cmd = digits[i]; i += 1
            if cmd in ("4", "8"):
                name = parse_sized_number()
                tokens.append(_Token("7", cmd, (name,)))
            else:
                tokens.append(_Token("7", cmd))

        elif d == "3":
            num = parse_sized_number()
            tokens.append(_Token("3", "", (num,)))

        elif d == "9":
            num = parse_sized_number()
            tokens.append(_Token("9", "", (num,)))

        elif d == "0":
            # Comment: find the next '0' to form the signature
            rest = digits[i:]
            j = rest.find("0")
            if j < 0:
                raise BespokeRuntimeError("Unterminated comment signature")
            sig = "0" + rest[: j + 1]  # e.g. "00" or "010"
            i += j + 1
            # Find end of comment body
            rest2 = digits[i:]
            k = rest2.find(sig)
            if k < 0:
                raise BespokeRuntimeError("Unterminated comment body")
            i += k + len(sig)  # skip body + closing signature

    return tokens


# ---------------------------------------------------------------------------
# Step 3 – token list → AST
# ---------------------------------------------------------------------------

def _create_ast(token_iter, block=None, inside_block=False):
    """
    Build an AST block from a shared token iterator.

    Sub-block types in the result:
      - IF:       [Token("7","2"), if_body_list, else_body_list]
      - WHILE:    [Token("7","5"), ...body..., Token("7","3")]
      - DOWHILE:  [Token("7","7"), ...body..., Token("7","3")]
      - FUNCTION: [Token("7","8",name), ...body..., Token("7","3")]
    """
    if block is None:
        block = []
    else:
        block = list(block)

    for token in token_iter:

        # CONTROL IF
        if token.cat == "7" and token.cmd == "2":
            if_block = list(_create_ast(token_iter, [token], inside_block=True))[1:]
            last = if_block.pop() if if_block else None

            if last and isinstance(last, _Token) and last.cat == "7" and last.cmd == "9":
                # CONTROL OTHERWISE → get the else body
                else_block = list(_create_ast(token_iter, [last], inside_block=True))[1:]
                if else_block:
                    else_block.pop()  # remove CONTROL END
            else:
                else_block = []

            block.append([token, if_block, else_block])

        # CONTROL END
        elif token.cat == "7" and token.cmd == "3":
            if not inside_block:
                raise BespokeRuntimeError("Unexpected CONTROL END")
            block.append(token)
            break

        # CONTROL WHILE / DOWHILE / FUNCTION
        elif token.cat == "7" and token.cmd in ("5", "7", "8"):
            sub = _create_ast(token_iter, [token], inside_block=True)
            block.append(sub)

        # CONTROL OTHERWISE (inside IF parsing)
        elif token.cat == "7" and token.cmd == "9":
            if not block:
                raise BespokeRuntimeError("Unexpected CONTROL OTHERWISE")
            first = block[0]
            if not (isinstance(first, _Token) and first.cat == "7" and first.cmd == "2"):
                raise BespokeRuntimeError("Unexpected CONTROL OTHERWISE")
            block.append(token)
            break

        # CONTINUED – extends the args of the previous PUT/CALL/FUNCTION token
        elif token.cat == "9":
            if not block or not isinstance(block[-1], _Token):
                raise BespokeRuntimeError("Unexpected CONTINUED")
            prev = block[-1]
            if prev.cat == "3" or (prev.cat == "7" and prev.cmd in ("4", "8")):
                block[-1] = _Token(prev.cat, prev.cmd, prev.args + token.args)
            else:
                raise BespokeRuntimeError("CONTINUED after invalid token")

        else:
            block.append(token)

    else:
        # Loop exhausted without break → auto-close if inside a block
        if inside_block:
            block.append(_Token("7", "3"))

    return block


# ---------------------------------------------------------------------------
# Math helper
# ---------------------------------------------------------------------------

def _int_nth_root(x: int, n: int) -> int:
    """Integer nth root of x, rounded down (not truncated)."""
    if n <= 0:
        raise BespokeRuntimeError("n must be positive for root")
    if x == 0:
        return 0
    if x < 0:
        raise BespokeRuntimeError("Cannot take real root of negative number")
    q, r = x + 1, x
    while q > r:
        q, r = r, ((n - 1) * r + x // pow(r, n - 1)) // n
    return q


# ---------------------------------------------------------------------------
# Interpreter class
# ---------------------------------------------------------------------------

class _BespokeExecution:
    def __init__(self, source, input_text, max_steps, max_output, time_limit_s):
        self.stack = []
        self.heap = {}          # int → int
        self.functions = {}     # str → body list
        self.output_parts = []
        self.output_len = 0
        self.steps = 0
        self.max_steps = max_steps
        self.max_output = max_output
        self.time_limit_s = time_limit_s
        self.input_stream = StringIO(input_text)
        self.start = time.time()

        digits = convert_to_digits(source)
        if not digits:
            self.ast = []
            return
        tokens = _tokenize(digits)
        self.ast = _create_ast(iter(tokens))

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self):
        try:
            self._interpret_block(self.ast)
        except _EndProgramSignal:
            pass
        except _ReturnSignal:
            raise BespokeRuntimeError("RETURN outside of function")
        except _BreakSignal:
            raise BespokeRuntimeError("BREAK outside of loop")
        return {"output": "".join(self.output_parts), "steps": self.steps}

    # ------------------------------------------------------------------
    # Limits
    # ------------------------------------------------------------------

    def _check_limits(self):
        if self.steps > self.max_steps:
            raise BespokeRuntimeError("Execution stopped: max steps exceeded")
        if (time.time() - self.start) > self.time_limit_s:
            raise BespokeRuntimeError("Execution stopped: time limit exceeded")

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------

    def _peek_char(self):
        pos = self.input_stream.tell()
        ch = self.input_stream.read(1)
        if ch:
            self.input_stream.seek(pos)
        return ch

    def _read_number(self):
        while True:
            ch = self._peek_char()
            if ch and ch.isspace():
                self.input_stream.read(1)
            else:
                break
        buf = []
        ch = self._peek_char()
        if ch == "-":
            self.input_stream.read(1)
            buf.append("-")
        while True:
            ch = self._peek_char()
            if ch and ch.isdigit():
                self.input_stream.read(1)
                buf.append(ch)
            else:
                break
        if not buf or buf == ["-"]:
            raise BespokeRuntimeError("Invalid number input")
        return int("".join(buf))

    # ------------------------------------------------------------------
    # Output helper
    # ------------------------------------------------------------------

    def _write(self, s: str):
        self.output_len += len(s)
        if self.output_len > self.max_output:
            raise BespokeRuntimeError("Output limit exceeded")
        self.output_parts.append(s)

    # ------------------------------------------------------------------
    # Block interpreter
    # ------------------------------------------------------------------

    def _interpret_block(self, block):
        for item in block:
            self._check_limits()
            if isinstance(item, list):
                self._interpret_subblock(item)
            else:
                self.steps += 1
                self._handle_token(item)

    def _interpret_subblock(self, item):
        first = item[0]
        if not isinstance(first, _Token):
            raise BespokeRuntimeError("Invalid AST node")

        if first.cat != "7":
            raise BespokeRuntimeError(f"Unexpected sub-block category: {first.cat}")

        if first.cmd == "2":
            # CONTROL IF: [if_token, if_body, else_body]
            if not self.stack:
                raise BespokeRuntimeError("Stack underflow")
            cond = self.stack.pop()
            body = item[1] if cond else item[2]
            self._interpret_block(body)

        elif first.cmd == "5":
            # CONTROL WHILE: condition checked at top of each iteration
            body = item[1:-1]
            while True:
                self._check_limits()
                if not self.stack:
                    raise BespokeRuntimeError("Stack underflow")
                if not self.stack.pop():
                    break
                try:
                    self._interpret_block(body)
                except _BreakSignal:
                    break

        elif first.cmd == "7":
            # CONTROL DOWHILE: condition checked at bottom of each iteration
            body = item[1:-1]
            while True:
                try:
                    self._interpret_block(body)
                except _BreakSignal:
                    break
                self._check_limits()
                if not self.stack:
                    raise BespokeRuntimeError("Stack underflow")
                if not self.stack.pop():
                    break

        elif first.cmd == "8":
            # CONTROL FUNCTION: define, do not execute
            name = "".join(first.args)
            self.functions[name] = item[1:-1]

        else:
            raise BespokeRuntimeError(f"Unexpected CONTROL sub-block: {first.cmd}")

    # ------------------------------------------------------------------
    # Token handler
    # ------------------------------------------------------------------

    def _handle_token(self, token):
        cat = token.cat
        cmd = token.cmd
        stack = self.stack

        # ── Heap ──────────────────────────────────────────────────────
        if cat == "1":
            if cmd in "13579":   # H V  – load
                if not stack:
                    raise BespokeRuntimeError("Stack underflow")
                addr = stack.pop()
                stack.append(self.heap.get(addr, 0))
            elif cmd in "24680": # H SV – store
                if len(stack) < 2:
                    raise BespokeRuntimeError("Stack underflow")
                addr = stack.pop()
                val = stack.pop()
                self.heap[addr] = val

        # ── Stack manipulation ─────────────────────────────────────────
        elif cat == "2":
            if cmd == "1":      # DO P
                if not stack: raise BespokeRuntimeError("Stack underflow")
                stack.pop()

            elif cmd == "2":    # DO PN
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if n == 0 or abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                stack.pop(-n if n > 0 else -n - 1)

            elif cmd == "3":    # DO ROT
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if n == 0 or abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                if n > 0:
                    stack[-n:] = [stack[-1]] + stack[-n:-1]
                else:
                    stack[-n - 1:] = [stack[-1]] + stack[-n - 1:-1]

            elif cmd == "4":    # DO COPY
                if not stack: raise BespokeRuntimeError("Stack underflow")
                stack.append(stack[-1])

            elif cmd == "5":    # DO COPYN
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if n == 0 or abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                stack.append(stack[-n] if n > 0 else stack[-n - 1])

            elif cmd == "6":    # DO SWITCH
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                stack[-1], stack[-2] = stack[-2], stack[-1]

            elif cmd == "7":    # DO SWITCHN
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if n == 0 or abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                idx = -n if n > 0 else -n - 1
                stack[-1], stack[idx] = stack[idx], stack[-1]

            elif cmd == "8":    # DO TURNOVER
                stack.reverse()

            elif cmd == "9":    # DO TURNOVERN
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                if n > 0:
                    stack[-n:] = stack[:-n - 1:-1]
                elif n < 0:
                    stack[:-n] = stack[-n - 1::-1]

            elif cmd == "0":    # DO ROTINVERSE
                if not stack: raise BespokeRuntimeError("Stack underflow")
                n = stack.pop()
                if n == 0 or abs(n) > len(stack):
                    raise BespokeRuntimeError(f"Invalid stack argument: {n}")
                if n > 0:
                    stack[-n:] = stack[-n + 1:] + [stack[-n]]
                else:
                    stack[-n - 1:] = stack[-n:] + [stack[-n - 1]]

        # ── Push multi-digit number ────────────────────────────────────
        elif cat == "3":
            stack.append(int("".join(token.args)))

        # ── Push single-digit number ───────────────────────────────────
        elif cat == "4":
            stack.append(int(cmd))

        # ── Input ──────────────────────────────────────────────────────
        elif cat == "5":
            if cmd in "13579":   # INPUT N
                stack.append(self._read_number())
            elif cmd in "24680": # INPUT CH
                ch = self.input_stream.read(1)
                stack.append(ord(ch) if ch else -1)

        # ── Output ─────────────────────────────────────────────────────
        elif cat == "6":
            if cmd in "13579":   # OUTPUT N
                if not stack: raise BespokeRuntimeError("Stack underflow")
                self._write(str(stack.pop()))
            elif cmd in "24680": # OUTPUT CH
                if not stack: raise BespokeRuntimeError("Stack underflow")
                self._write(chr(stack.pop() % 0x110000))

        # ── Control flow ───────────────────────────────────────────────
        elif cat == "7":
            if cmd == "1":      # CONTROL B (break)
                raise _BreakSignal()

            elif cmd == "4":    # CONTROL CALL
                name = "".join(token.args)
                body = self.functions.get(name)
                if body is None:
                    raise BespokeRuntimeError(f"Undefined function: {name}")
                try:
                    self._interpret_block(body)
                except _ReturnSignal:
                    pass
                except _BreakSignal:
                    raise BespokeRuntimeError("BREAK outside of loop (inside function)")

            elif cmd == "6":    # CONTROL RETURN
                raise _ReturnSignal()

            elif cmd == "0":    # CONTROL ENDPROGRAM
                raise _EndProgramSignal()

        # ── Stack arithmetic / operations ──────────────────────────────
        elif cat == "8":
            if cmd == "1":      # STACKTOP F
                if not stack: raise BespokeRuntimeError("Stack underflow")
                stack.append(int(not stack.pop()))

            elif cmd == "2":    # STACKTOP LT
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop(); a = stack.pop()
                stack.append(int(a < b))

            elif cmd == "3":    # STACKTOP POW
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop(); a = stack.pop()
                if a < 0 and b < 0:
                    raise BespokeRuntimeError("Both base and exponent cannot be negative")
                if b >= 0:
                    stack.append(a ** b)
                else:
                    stack.append(_int_nth_root(a, -b))

            elif cmd == "4":    # STACKTOP PLUS
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop(); a = stack.pop()
                stack.append(a + b)

            elif cmd == "5":    # STACKTOP MINUS
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop(); a = stack.pop()
                stack.append(a - b)

            elif cmd == "6":    # STACKTOP MODULO
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop()
                if not b:
                    raise BespokeRuntimeError("Modulo by zero")
                a = stack.pop()
                stack.append(a % b)

            elif cmd == "7":    # STACKTOP PLUSONE
                if not stack: raise BespokeRuntimeError("Stack underflow")
                stack[-1] += 1

            elif cmd == "8":    # STACKTOP MINUSONE
                if not stack: raise BespokeRuntimeError("Stack underflow")
                stack[-1] -= 1

            elif cmd == "9":    # STACKTOP PRODUCTOF
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop(); a = stack.pop()
                stack.append(a * b)

            elif cmd == "0":    # STACKTOP QUOTIENTOF (floor division)
                if len(stack) < 2: raise BespokeRuntimeError("Stack underflow")
                b = stack.pop()
                if not b:
                    raise BespokeRuntimeError("Division by zero")
                a = stack.pop()
                stack.append(a // b)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_bespoke(
    source: str,
    input_text: str = "",
    max_steps: int = 500_000,
    max_output: int = 100_000,
    time_limit_s: float = 5.0,
) -> dict:
    """
    Run a Bespoke program.

    Returns
    -------
    dict with keys:
        "output" (str): the program's stdout
        "steps"  (int): number of instructions executed

    Raises
    ------
    BespokeRuntimeError on any runtime or parse error.
    """
    exec_ = _BespokeExecution(source, input_text, max_steps, max_output, time_limit_s)
    return exec_.run()
