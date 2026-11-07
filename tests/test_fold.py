"""
Test for fold (saddle-node) bifurcation (gamma<1, Thevenin source).
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_fold():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "fold"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "fold" in data, "fold missing from results.json"

    # Check that critical conductance g_c and critical field E_c are present
    fc = data["fold"].get("g_c")
    Ec = data["fold"].get("E_c")
    assert fc is not None and isinstance(fc, float), "g_c missing or not float"
    assert Ec is not None and isinstance(Ec, float), "E_c missing or not float"

    print("test_fold PASSED")


if __name__ == "__main__":
    test_fold()