import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable
SCRIPT = os.path.join(ROOT, "poetic.py")
TEST_PROGRAM = os.path.join(ROOT, "examples", "hello.ptc")

proc = subprocess.run([PY, SCRIPT, TEST_PROGRAM], capture_output=True, text=True)
print("STDOUT:", proc.stdout)
print("STDERR:", proc.stderr)

if proc.returncode != 0:
    print("Test failed: non-zero exit code", proc.returncode)
    sys.exit(2)

expected = "Hello World!"
if proc.stdout.strip() != expected:
    print(f"Test failed: expected '{expected}', got '{proc.stdout.strip()}'")
    sys.exit(1)

print("Test passed")
