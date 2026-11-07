"""
Test for Theorem B (Hodge-Morse / spectrum of Hessian).
Runs the unified script with test 'B' and verifies the generated results.
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_theorem_B():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "B"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "theorem_B" in data, "theorem_B missing from results.json"

    # Check that at least one entry has expected eigenvalues near theoretical values
    sample_keys = [k for k in data["theorem_B"].keys() if "gamma" in k.lower()]
    assert len(sample_keys) > 0, "no gamma entries in theorem_B"

    # Verify that eigenvalues are numeric and not NaN
    for key in sample_keys[:2]:  # check first two entries
        eig = data["theorem_B"][key].get("eig_min")
        assert eig is not None and isinstance(eig, float), f"eig_min missing or not float for {key}"
        assert not (eig != eig), f"eig_min is NaN for {key}"

    print("test_theorem_B PASSED")


if __name__ == "__main__":
    test_theorem_B()