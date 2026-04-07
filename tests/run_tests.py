import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable
SCRIPT = os.path.join(ROOT, "bespoke.py")


def run_case(program_name, input_text, expected):
    program = os.path.join(ROOT, "examples", program_name)
    proc = subprocess.run(
        [PY, SCRIPT, program],
        input=input_text,
        capture_output=True,
        text=True,
    )
    print(f"[{program_name}] STDOUT:", proc.stdout)
    print(f"[{program_name}] STDERR:", proc.stderr)

    if proc.returncode != 0:
        print(f"Test failed ({program_name}): non-zero exit code", proc.returncode)
        sys.exit(2)

    got = proc.stdout.strip()
    if got != expected:
        print(f"Test failed ({program_name}): expected '{expected}', got '{got}'")
        sys.exit(1)

    print(f"{program_name} test passed")


run_case("helloworld.bspk", "", "Hello, World!")
run_case("sum_two_numbers.bspk", "12 23", "35")
run_case("truth.bspk", "0", "0")

print("All Bespoke tests passed")
