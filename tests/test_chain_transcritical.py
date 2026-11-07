"""
Test for transcritical bifurcation in a chain (Dirichlet + linear cost c).
"""
import subprocess
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "codigo"
RES_FILE = CODE_DIR / "results.json"
SCRIPT = CODE_DIR / "otra_unified.py"


def test_chain_transcritical():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "chain"],
        cwd=str(CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Script failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"

    assert RES_FILE.exists(), "results.json not generated"

    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "chain_transcritical" in data, "chain_transcritical missing from results.json"

    # Verify that each N (1-4) has a max_abs_err entry
    for n_str in ["1", "2", "3", "4"]:
        assert n_str in data["chain_transcritical"], f"N={n_str} missing"
        err = data["chain_transcritical"][n_str].get("max_abs_err")
        assert err is not None and isinstance(err, float), f"max_abs_err missing for N={n_str}"

    print("test_chain_transcritical PASSED")


if __name__ == "__main__":
    test_chain_transcritical()