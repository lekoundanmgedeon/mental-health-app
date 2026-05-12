"""Run all command-line ML tests in order.

Usage:
    python scripts/04_run_all_prediction_tests.py
"""

from __future__ import annotations

import subprocess
import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def run_script(script_name: str) -> None:
    script_path = ROOT_DIR / "scripts" / script_name
    print(f"\n>>> Running {script_name}")
    try:
        subprocess.run([sys.executable, str(script_path)], cwd=ROOT_DIR, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"\nTest stopped because {script_name} failed.")
        print("Check that your real .pkl files are inside model_artifacts/ and run pip install -r requirements.txt.")
        raise SystemExit(exc.returncode) from exc


def main() -> None:
    run_script("01_inspect_model_artifacts.py")
    run_script("02_test_single_prediction.py")
    run_script("03_test_batch_predictions.py")
    print("\nAll prediction tests completed successfully.")


if __name__ == "__main__":
    main()
