"""Check the local Python environment before loading the ML model.

Usage:
    python scripts/00_check_environment.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT_DIR / "model_artifacts"


def safe_version(package_name: str) -> str:
    try:
        from importlib.metadata import version
        return version(package_name)
    except Exception as exc:
        return f"not installed ({exc})"


def main() -> None:
    print("=" * 72)
    print("ENVIRONMENT CHECK")
    print("=" * 72)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Project root: {ROOT_DIR}")
    print(f"Model directory: {MODEL_DIR}")
    print()
    print("Package versions:")
    for package in ["scikit-learn", "joblib", "numpy", "pandas", "flask"]:
        print(f"  - {package}: {safe_version(package)}")
    print()
    print("Expected model artifact files:")
    for filename in [
        "student_stress_model.pkl",
        "label_encoder_degree.pkl",
        "model_metadata.pkl",
        "model_metadata.json",
    ]:
        path = MODEL_DIR / filename
        status = "FOUND" if path.exists() else "missing"
        size = f" ({path.stat().st_size} bytes)" if path.exists() else ""
        print(f"  - {filename}: {status}{size}")
    print("=" * 72)


if __name__ == "__main__":
    main()
