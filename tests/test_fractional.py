"""
Test for fractional memory (Caputo) relaxation.
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_fractional():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "frac"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "fractional" in data, "fractional missing from results.json"

    # Verify that entries for alpha = 1.0, 0.9, 0.7, 0.5 exist
    for a in ["1.0", "0.9", "0.7", "0.5"]:
        assert a in data["fractional"], f"alpha={a} missing"
        entry = data["fractional"][a]
        assert "F_monotone" in entry, f"F_monotone missing for alpha={a}"
        # late_slope may be None (alpha=1) or a float
        if entry.get("late_slope") is not None:
            assert isinstance(entry["late_slope"], float), f"late_slope not float for alpha={a}"

    print("test_fractional PASSED")


if __name__ == "__main__":
    test_fractional()