#!/usr/bin/env python3
"""
Bespoke CLI interpreter.

Usage:
    bespoke.py [-i input-file] program.bspk
"""
import argparse
import sys

try:
    from tools.bespoke_engine import BespokeRuntimeError, run_bespoke
except ImportError:
    from bespoke_engine import BespokeRuntimeError, run_bespoke


def error(msg: str):
    sys.stderr.write(f"\nERROR: {msg}\n")
    sys.exit(1)


parser = argparse.ArgumentParser(description="Run a Bespoke program.")
parser.add_argument("program", help="Bespoke source file (.bspk)")
parser.add_argument(
    "-i", "--input",
    metavar="inputFile",
    help="take input from the specified file",
    required=False,
)
args = parser.parse_args()

# Read source
try:
    with open(args.program, encoding="utf-8") as f:
        source = f.read()
except FileNotFoundError:
    error(f"Program file not found: {args.program}")

# Read input
if args.input is None:
    input_text = sys.stdin.read()
else:
    try:
        with open(args.input, encoding="utf-8") as f:
            input_text = f.read()
    except FileNotFoundError:
        error(f"Input file not found: {args.input}")

# Run
try:
    result = run_bespoke(source=source, input_text=input_text)
    sys.stdout.write(result["output"])
    if not result["output"].endswith("\n"):
        sys.stdout.write("\n")
except BespokeRuntimeError as exc:
    error(str(exc))
