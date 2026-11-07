"""
Test for Theorem C.
Runs the unified script with test 'C' and verifies the generated results.
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_theorem_C():
    # Run the unified script with test 'C'
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "C"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    # Check that results.json was created
    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Theorem C should be present
    assert "theorem_C" in data, "theorem_C missing from results.json"

    print("test_theorem_C PASSED")


if __name__ == "__main__":
    test_theorem_C()