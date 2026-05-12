"""Inspect the real ML artifacts before using the web interface.

Usage:
    python scripts/01_inspect_model_artifacts.py
"""

from __future__ import annotations

from pathlib import Path
import sys
import traceback

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts._prediction_test_helpers import load_artifacts_direct, metadata_features


def main() -> None:
    model, degree_encoder, metadata = load_artifacts_direct()

    print("=" * 72)
    print("MODEL ARTIFACT INSPECTION")
    print("=" * 72)
    print(f"Model type: {type(model).__name__}")
    print(f"Metadata type: {type(metadata).__name__}")
    print(f"Metadata keys: {sorted([str(key) for key in metadata.keys()])}")

    features = metadata_features(metadata)
    print(f"Number of features: {len(features)}")
    for index, feature in enumerate(features, start=1):
        print(f"  {index:02d}. {feature}")

    if hasattr(model, "classes_"):
        print(f"Model classes: {list(model.classes_)}")
    else:
        print("Model classes: not exposed by this estimator")

    if hasattr(model, "predict_proba"):
        print("Probability support: YES, predict_proba() is available")
    else:
        print("Probability support: NO, predict_proba() is not available")

    if hasattr(degree_encoder, "classes_"):
        print(f"Degree encoder classes: {list(degree_encoder.classes_)}")
    else:
        print("Degree encoder classes: not exposed by this encoder")

    metrics = metadata.get("metrics") or {}
    if metrics:
        print("Model metrics from metadata:")
        for name, value in metrics.items():
            print(f"  - {name}: {value}")

    print("=" * 72)
    print("Inspection completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("=" * 72)
        print("ERROR DURING MODEL INSPECTION")
        print("=" * 72)
        print(f"Error type: {type(exc).__name__}")
        print(f"Error message: {exc!r}")
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 72)
        raise SystemExit(1)
