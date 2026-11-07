"""
Test for Theorem A (Lyapunov / convergence global).
Runs the unified script with test 'A' and verifies the generated results.
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_theorem_A():
    # Run the unified script with test 'A'
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "A"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    # Check that results.json was created
    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Theorem A should be present
    assert "theorem_A" in data, "theorem_A missing from results.json"

    # Check that at least one mode has max_dF_dt_positive ~= 0 (convergence)
    for mode, vals in data["theorem_A"].items():
        # max_dF_dt_positive should be 0 or very small (numerical tolerance)
        assert vals["max_dF_dt_positive"] == 0.0, (
            f"max_dF_dt_positive not zero for mode {mode}: {vals['max_dF_dt_positive']}"
        )

    print("test_theorem_A PASSED")


if __name__ == "__main__":
    test_theorem_A()