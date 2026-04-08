import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable
SCRIPT = os.path.join(ROOT, "poetic.py")
TEST_PROGRAM = os.path.join(ROOT, "examples", "poetic", "hello.ptc")
TEST_BONJOUR = os.path.join(ROOT, "examples", "poetic", "bonjour.ptc")

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

# --- bonjour test (wimpmode)
proc = subprocess.run([PY, SCRIPT, "-w", TEST_BONJOUR], capture_output=True, text=True)
print("STDOUT:", proc.stdout)
print("STDERR:", proc.stderr)

if proc.returncode != 0:
    print("Test failed (bonjour): non-zero exit code", proc.returncode)
    sys.exit(2)

expected = "bonjour!"
if proc.stdout.strip() != expected:
    print(f"Test failed (bonjour): expected '{expected}', got '{proc.stdout.strip()}'")
    sys.exit(1)

print("Bonjour test passed")
