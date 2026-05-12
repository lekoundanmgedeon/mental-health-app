"""Run one command-line prediction without opening the web interface.

Usage:
    python scripts/02_test_single_prediction.py
    python scripts/02_test_single_prediction.py --profile high_risk
    python scripts/02_test_single_prediction.py --profile balanced_student

The result is written to:
    outputs/single_prediction_result.json
"""

from __future__ import annotations

from pathlib import Path
import sys
import traceback

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
from pathlib import Path

from scripts._prediction_test_helpers import (
    OUTPUT_DIR,
    TEST_INPUT_DIR,
    print_probability_block,
    read_json,
    run_prediction_for_profile,
    write_json,
)


DEFAULT_PROFILE_NAME = "balanced_student"


def load_named_profile(profile_name: str) -> dict:
    profiles_path = TEST_INPUT_DIR / "sample_profiles.json"
    profiles = read_json(profiles_path)

    for profile in profiles:
        if profile.get("profile_name") == profile_name:
            return profile

    available = [profile.get("profile_name") for profile in profiles]
    raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {available}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one ML prediction from the command line.")
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE_NAME,
        help="Profile name from tests/test_inputs/sample_profiles.json",
    )
    args = parser.parse_args()

    profile = load_named_profile(args.profile)
    result = run_prediction_for_profile(profile)

    output_path = OUTPUT_DIR / "single_prediction_result.json"
    write_json(output_path, result)

    print("=" * 72)
    print("SINGLE PREDICTION TEST")
    print("=" * 72)
    print(f"Profile: {args.profile}")
    print(f"Predicted class: {result['predicted_class']}")
    print(f"Overall risk score: {result['overall_score']}%")
    print_probability_block(result.get("probabilities", {}))
    print(f"Explanation: {result['explanation']}")
    print(f"Output file: {Path(output_path).as_posix()}")
    print("=" * 72)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR:", repr(exc))
        traceback.print_exc()
        raise SystemExit(1)
