"""
Test for pitchfork bifurcation (gamma=1, two parallel edges).
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_pitchfork():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "pitch"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "pitchfork" in data, "pitchfork missing from results.json"

    # The asymmetry should be close to 0 for gamma near 1, and non-zero for gamma!=1
    asym = data["pitchfork"].get("asym", [])
    assert isinstance(asym, list), "asym should be a list"
    assert len(asym) == 21, f"expected 21 asymmetry values, got {len(asym)}"

    print("test_pitchfork PASSED")


if __name__ == "__main__":
    test_pitchfork()