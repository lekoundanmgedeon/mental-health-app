"""Run several command-line predictions before testing the Flask UI.

Usage:
    python scripts/03_test_batch_predictions.py

Inputs:
    tests/test_inputs/sample_profiles.json

Outputs:
    outputs/batch_prediction_results.json
    outputs/batch_prediction_results.csv
"""

from __future__ import annotations

from pathlib import Path
import sys
import traceback

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import csv
from pathlib import Path

from scripts._prediction_test_helpers import (
    OUTPUT_DIR,
    TEST_INPUT_DIR,
    print_probability_block,
    read_json,
    run_prediction_for_profile,
    write_json,
)


def main() -> None:
    profiles_path = TEST_INPUT_DIR / "sample_profiles.json"
    profiles = read_json(profiles_path)

    results = []

    print("=" * 72)
    print("BATCH PREDICTION TEST")
    print("=" * 72)

    for profile in profiles:
        profile_name = profile.get("profile_name", "unnamed_profile")
        result = run_prediction_for_profile(profile)
        results.append(result)

        print(f"\nProfile: {profile_name}")
        print(f"Predicted class: {result['predicted_class']}")
        print(f"Overall risk score: {result['overall_score']}%")
        print_probability_block(result.get("probabilities", {}))

    json_output = OUTPUT_DIR / "batch_prediction_results.json"
    csv_output = OUTPUT_DIR / "batch_prediction_results.csv"
    write_json(json_output, results)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(csv_output, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "profile_name",
                "predicted_class",
                "overall_score",
                "no_depression_probability",
                "depression_probability",
                "degree",
                "age",
                "academic_pressure",
                "financial_stress",
                "suicidal_thoughts",
            ],
        )
        writer.writeheader()
        for result in results:
            submitted = result.get("submitted_profile", {})
            probabilities = result.get("probabilities", {})
            no_dep = next((value for label, value in probabilities.items() if "no depression" in label.lower()), None)
            dep = next((value for label, value in probabilities.items() if "possible depression" in label.lower()), None)
            writer.writerow(
                {
                    "profile_name": submitted.get("profile_name"),
                    "predicted_class": result.get("predicted_class"),
                    "overall_score": result.get("overall_score"),
                    "no_depression_probability": no_dep,
                    "depression_probability": dep,
                    "degree": submitted.get("degree"),
                    "age": submitted.get("age"),
                    "academic_pressure": submitted.get("academic_pressure"),
                    "financial_stress": submitted.get("financial_stress"),
                    "suicidal_thoughts": submitted.get("suicidal_thoughts"),
                }
            )

    print("\n" + "=" * 72)
    print("Batch test completed successfully.")
    print(f"JSON output: {Path(json_output).as_posix()}")
    print(f"CSV output:  {Path(csv_output).as_posix()}")
    print("=" * 72)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR:", repr(exc))
        traceback.print_exc()
        raise SystemExit(1)
