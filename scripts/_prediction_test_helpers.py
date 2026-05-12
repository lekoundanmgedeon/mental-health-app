"""Standalone helpers for command-line ML prediction tests.

These scripts intentionally do not import Flask. They let you validate the real
model artifacts before testing the web interface.
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

try:
    import sklearn
    from sklearn.exceptions import InconsistentVersionWarning
except Exception:  # pragma: no cover
    sklearn = None
    InconsistentVersionWarning = None  # type: ignore

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT_DIR / "model_artifacts"
OUTPUT_DIR = ROOT_DIR / "outputs"
TEST_INPUT_DIR = ROOT_DIR / "tests" / "test_inputs"

DEFAULT_FEATURE_ORDER = [
    "Age",
    "Gender Num",
    "Academic Pressure",
    "Work Pressure",
    "CGPA",
    "Study Satisfaction",
    "Job Satisfaction",
    "Sleep Duration Num",
    "Dietary Habits Num",
    "Suicidal Thoughts",
    "Work/Study Hours",
    "Financial Stress",
    "Family History",
    "Degree Num",
]

DEFAULT_SLEEP_MAP = {
    "Less than 5 hours": 4.0,
    "5-6 hours": 5.5,
    "6-7 hours": 6.5,
    "7-8 hours": 7.5,
    "More than 8 hours": 9.0,
}

DEFAULT_DIETARY_MAP = {
    "Unhealthy": 1,
    "Moderate": 2,
    "Healthy": 3,
}

BINARY_CLASS_LABELS = {
    0: "No depression risk detected",
    1: "Possible depression risk",
    "0": "No depression risk detected",
    "1": "Possible depression risk",
}


def first_existing_file(filenames: list[str]) -> Path | None:
    """Return the first existing artifact path from model_artifacts/."""
    for filename in filenames:
        path = MODEL_DIR / filename
        if path.exists():
            return path
    return None


def read_json(path: Path) -> Any:
    """Read a JSON file using UTF-8."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Write formatted JSON using UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def joblib_load_with_version_warning(path: Path) -> Any:
    """Load a joblib artifact and keep version warnings visible."""
    if InconsistentVersionWarning is None:
        return joblib.load(path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InconsistentVersionWarning)
        obj = joblib.load(path)

    for warning in caught:
        if issubclass(warning.category, InconsistentVersionWarning):
            print(f"WARNING: {warning.message}")
            print("TIP: install the same scikit-learn version used during training, usually scikit-learn==1.6.1 for these artifacts.")

    return obj


def load_pickle_or_json_metadata(path: Path) -> dict[str, Any]:
    """Load metadata from .pkl/.joblib/.json, with fallback for renamed JSON files."""
    if path.suffix.lower() == ".json":
        metadata = read_json(path)
    else:
        try:
            metadata = joblib_load_with_version_warning(path)
        except Exception as joblib_error:
            try:
                metadata = read_json(path)
            except Exception as json_error:
                raise RuntimeError(
                    f"Could not load metadata file {path.name}. "
                    f"joblib error: {joblib_error}. JSON fallback error: {json_error}."
                ) from joblib_error

    if isinstance(metadata, bytes):
        metadata = json.loads(metadata.decode("utf-8"))
    elif isinstance(metadata, str):
        metadata = json.loads(metadata)

    if not isinstance(metadata, dict):
        raise TypeError(
            f"Metadata must be a dict, got {type(metadata).__name__}. "
            f"Value preview: {repr(metadata)[:200]}"
        )

    return metadata


def load_metadata() -> dict[str, Any]:
    """Load model metadata from .pkl, .joblib, or .json."""
    metadata_path = first_existing_file([
        "model_metadata.pkl",
        "model_metadata.joblib",
        "model_metadata.json",
    ])
    if metadata_path is None:
        print("WARNING: metadata file not found; using default feature order.")
        return {
            "features": DEFAULT_FEATURE_ORDER,
            "sleep_map": DEFAULT_SLEEP_MAP,
            "dietary_map": DEFAULT_DIETARY_MAP,
            "target": "Depression (0=No, 1=Yes)",
        }

    return load_pickle_or_json_metadata(metadata_path)


def load_artifacts_direct() -> tuple[Any, Any, dict[str, Any]]:
    """Load the model, degree encoder, and metadata without Flask."""
    model_path = first_existing_file([
        "student_stress_model.pkl",
        "student_stress_model.joblib",
    ])
    degree_encoder_path = first_existing_file([
        "label_encoder_degree.pkl",
        "label_encoder_degree.joblib",
    ])

    missing = []
    if model_path is None:
        missing.append("student_stress_model.pkl")
    if degree_encoder_path is None:
        missing.append("label_encoder_degree.pkl")

    if missing:
        raise FileNotFoundError(
            "Missing ML artifact(s): "
            + ", ".join(missing)
            + ". Put the real files inside model_artifacts/."
        )

    print(f"Loading model: {model_path}")
    model = joblib_load_with_version_warning(model_path)

    print(f"Loading degree encoder: {degree_encoder_path}")
    degree_encoder = joblib_load_with_version_warning(degree_encoder_path)

    metadata = load_metadata()
    return model, degree_encoder, metadata


def metadata_features(metadata: dict[str, Any]) -> list[str]:
    """Read feature order from metadata."""
    features = metadata.get("features") or metadata.get("feature_names") or metadata.get("columns")
    if isinstance(features, list) and features:
        return [str(feature) for feature in features]
    return DEFAULT_FEATURE_ORDER


def get_sleep_map(metadata: dict[str, Any]) -> dict[str, float]:
    """Return sleep mapping from metadata."""
    sleep_map = metadata.get("sleep_map") or DEFAULT_SLEEP_MAP
    return {str(key).strip("'"): float(value) for key, value in sleep_map.items()}


def get_dietary_map(metadata: dict[str, Any]) -> dict[str, int]:
    """Return dietary habit mapping from metadata."""
    dietary_map = metadata.get("dietary_map") or DEFAULT_DIETARY_MAP
    return {str(key): int(value) for key, value in dietary_map.items()}


def clean_number(value: Any, default: float = 0.0) -> float:
    """Convert a value into a finite float."""
    try:
        number = float(value)
        if not math.isfinite(number):
            return default
        return number
    except (TypeError, ValueError):
        return default


def clean_int(value: Any, default: int = 0) -> int:
    """Convert a value into an integer."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def get_valid_degree_value(degree_encoder: Any, preferred_value: str | None = None) -> str:
    """Return a value accepted by label_encoder_degree.pkl."""
    degree_values = [str(value) for value in getattr(degree_encoder, "classes_", [])]
    if not degree_values:
        raise RuntimeError("No degree values found. Check label_encoder_degree.pkl.")

    if preferred_value and preferred_value in degree_values:
        return preferred_value

    return degree_values[0]


def encode_degree(value: str, degree_encoder: Any) -> int:
    """Encode degree using the same encoder as training."""
    if not hasattr(degree_encoder, "transform"):
        raise TypeError("label_encoder_degree.pkl must provide transform().")

    try:
        return int(degree_encoder.transform([value])[0])
    except Exception as exc:
        allowed = [str(item) for item in getattr(degree_encoder, "classes_", [])]
        raise ValueError(f"Unknown degree value: {value}. Allowed values: {allowed}") from exc


def normalize_test_profile(profile: dict[str, Any], degree_encoder: Any) -> dict[str, Any]:
    """Prepare one test profile before prediction."""
    normalized = dict(profile)
    degree = normalized.get("degree")

    if degree in (None, "", "__AUTO_FIRST__"):
        normalized["degree"] = get_valid_degree_value(degree_encoder)
    else:
        normalized["degree"] = get_valid_degree_value(degree_encoder, str(degree))

    return normalized


def build_model_input(profile: dict[str, Any], degree_encoder: Any, metadata: dict[str, Any]) -> dict[str, float]:
    """Convert form-style fields into the exact model feature names."""
    sleep_map = get_sleep_map(metadata)
    dietary_map = get_dietary_map(metadata)

    sleep_value = str(profile.get("sleep_duration", "")).strip()
    dietary_value = str(profile.get("dietary_habits", "")).strip()

    if sleep_value not in sleep_map:
        raise ValueError(f"Unknown sleep duration: {sleep_value}. Allowed values: {list(sleep_map.keys())}")
    if dietary_value not in dietary_map:
        raise ValueError(f"Unknown dietary habit: {dietary_value}. Allowed values: {list(dietary_map.keys())}")

    return {
        "Age": clean_int(profile.get("age")),
        "Gender Num": clean_int(profile.get("gender")),
        "Academic Pressure": clean_int(profile.get("academic_pressure")),
        "Work Pressure": clean_int(profile.get("work_pressure")),
        "CGPA": clean_number(profile.get("cgpa")),
        "Study Satisfaction": clean_int(profile.get("study_satisfaction")),
        "Job Satisfaction": clean_int(profile.get("job_satisfaction")),
        "Sleep Duration Num": sleep_map[sleep_value],
        "Dietary Habits Num": dietary_map[dietary_value],
        "Suicidal Thoughts": clean_int(profile.get("suicidal_thoughts")),
        "Work/Study Hours": clean_number(profile.get("work_study_hours")),
        "Financial Stress": clean_int(profile.get("financial_stress")),
        "Family History": clean_int(profile.get("family_history")),
        "Degree Num": encode_degree(str(profile.get("degree", "")).strip(), degree_encoder),
    }


def label_for_class(raw_class: Any) -> str:
    """Convert binary class output into a readable label."""
    return BINARY_CLASS_LABELS.get(raw_class, BINARY_CLASS_LABELS.get(str(raw_class), str(raw_class)))


def build_probability_dict(model: Any, processed_input: pd.DataFrame) -> dict[str, float]:
    """Return probability percentages for each class."""
    if not hasattr(model, "predict_proba"):
        return {}

    raw_probabilities = model.predict_proba(processed_input)[0]
    classes = list(getattr(model, "classes_", range(len(raw_probabilities))))
    return {
        label_for_class(classes[index]): round(float(probability) * 100, 2)
        for index, probability in enumerate(raw_probabilities)
    }


def calculate_risk_score(probabilities: dict[str, float], predicted_class: str) -> float:
    """Use class-1 probability as risk score when available."""
    for label, value in probabilities.items():
        if "possible depression" in label.lower() or "depression risk" in label.lower():
            return round(float(value), 1)
    return 100.0 if "possible" in predicted_class.lower() else 0.0


def build_explanation(predicted_class: str, model_input: dict[str, float]) -> str:
    """Create a simple explanation from the strongest submitted signals."""
    reasons: list[str] = []

    if model_input.get("Suicidal Thoughts") == 1:
        reasons.append("reported suicidal thoughts")
    if model_input.get("Academic Pressure", 0) >= 4:
        reasons.append("high academic pressure")
    if model_input.get("Financial Stress", 0) >= 4:
        reasons.append("high financial stress")
    if model_input.get("Work/Study Hours", 0) >= 9:
        reasons.append("long work/study hours")
    if model_input.get("Sleep Duration Num", 8) < 6:
        reasons.append("short sleep duration")
    if model_input.get("Study Satisfaction", 5) <= 2:
        reasons.append("low study satisfaction")
    if model_input.get("Dietary Habits Num", 3) <= 1:
        reasons.append("unhealthy dietary habits")
    if model_input.get("Family History") == 1:
        reasons.append("family history of mental illness")

    if reasons:
        return f"Prediction: {predicted_class}. Main submitted signals: {', '.join(reasons[:5])}."
    return f"Prediction: {predicted_class}. No strong risk signal was detected in the submitted test profile."


def run_prediction_for_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Run one prediction directly from the saved model artifacts."""
    model, degree_encoder, metadata = load_artifacts_direct()
    normalized_profile = normalize_test_profile(profile, degree_encoder)
    feature_order = metadata_features(metadata)
    model_input = build_model_input(normalized_profile, degree_encoder, metadata)

    missing_features = [feature for feature in feature_order if feature not in model_input]
    if missing_features:
        raise ValueError(f"Missing required model feature(s): {missing_features}")

    processed_input = pd.DataFrame([model_input], columns=feature_order)
    raw_prediction = model.predict(processed_input)[0]
    predicted_class = label_for_class(raw_prediction)
    probabilities = build_probability_dict(model, processed_input)

    if not probabilities:
        probabilities = {predicted_class: 100.0}

    return {
        "profile_name": normalized_profile.get("profile_name", "unnamed_profile"),
        "predicted_class": predicted_class,
        "overall_score": calculate_risk_score(probabilities, predicted_class),
        "probabilities": probabilities,
        "explanation": build_explanation(predicted_class, model_input),
        "submitted_profile": normalized_profile,
        "model_input": model_input,
        "feature_order": feature_order,
    }


def print_probability_block(probabilities: dict[str, float]) -> None:
    """Print probabilities line by line."""
    if not probabilities:
        print("Probabilities: not available for this model")
        return

    print("Probabilities:")
    for label, value in probabilities.items():
        print(f"  - {label}: {value:.2f}%")
