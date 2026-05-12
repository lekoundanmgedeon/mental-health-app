"""Machine Learning prediction service for the real student depression model.

Expected real artifacts inside model_artifacts/:
- student_stress_model.pkl          main trained classifier
- label_encoder_degree.pkl          encoder used for the Degree column
- model_metadata.pkl or .json       metadata containing feature order and mappings

The service converts user-friendly form fields into the exact model features:
Age, Gender Num, Academic Pressure, Work Pressure, CGPA, Study Satisfaction,
Job Satisfaction, Sleep Duration Num, Dietary Habits Num, Suicidal Thoughts,
Work/Study Hours, Financial Stress, Family History, Degree Num.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from flask import current_app


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

FALLBACK_DEGREE_CHOICES = [
    "Class 12",
    "Diploma",
    "Bachelor",
    "B.Tech",
    "BSc",
    "BA",
    "B.Com",
    "M.Tech",
    "MSc",
    "MA",
    "MBA",
    "PhD",
]


class MLServiceError(RuntimeError):
    """Raised when ML artifacts or prediction logic fail."""


_MODEL_CACHE: dict[str, Any] = {}


def _artifact_path(filename: str) -> Path:
    """Return the absolute path of a model artifact."""
    return Path(current_app.config["MODEL_DIR"]) / filename


def _first_existing_file(filenames: list[str]) -> Path | None:
    """Return the first existing artifact path from a list of possible names."""
    for filename in filenames:
        path = _artifact_path(filename)
        if path.exists():
            return path
    return None


def _default_metadata() -> dict[str, Any]:
    """Return safe metadata when no metadata artifact is available."""
    return {
        "features": DEFAULT_FEATURE_ORDER,
        "sleep_map": DEFAULT_SLEEP_MAP,
        "dietary_map": DEFAULT_DIETARY_MAP,
        "target": "Depression (0=No, 1=Yes)",
    }


def _read_metadata_as_json(path: Path) -> dict[str, Any]:
    """Read metadata as JSON, even if the file extension is .pkl."""
    with open(path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, dict):
        raise TypeError(f"Metadata JSON must contain an object/dict, got {type(metadata).__name__}.")

    return metadata


def _coerce_metadata_to_dict(raw_metadata: Any, source_name: str) -> dict[str, Any]:
    """Convert loaded metadata into a Python dict and reject invalid values."""
    metadata = raw_metadata

    if isinstance(metadata, bytes):
        metadata = json.loads(metadata.decode("utf-8"))
    elif isinstance(metadata, str):
        stripped = metadata.strip()
        if stripped.startswith("{"):
            metadata = json.loads(stripped)

    if not isinstance(metadata, dict):
        raise TypeError(
            f"Metadata file {source_name} must contain a dict. "
            f"Got {type(metadata).__name__}: {repr(metadata)[:120]}"
        )

    return metadata


def _load_metadata_file(path: Path) -> dict[str, Any]:
    """Load one metadata file. Supports real joblib/pickle and JSON renamed as .pkl."""
    if path.suffix.lower() == ".json":
        return _read_metadata_as_json(path)

    try:
        raw_metadata = joblib.load(path)
        return _coerce_metadata_to_dict(raw_metadata, path.name)
    except Exception as joblib_error:
        # Some users receive model_metadata.pkl even though the content is JSON.
        # In that case, joblib can fail with a non-explicit error such as "123"
        # because the first JSON character is "{" (ASCII 123).
        try:
            return _read_metadata_as_json(path)
        except Exception as json_error:
            raise MLServiceError(
                f"Unable to load metadata file {path.name}. "
                f"joblib error: {joblib_error}. JSON fallback error: {json_error}."
            ) from joblib_error


def _load_metadata() -> dict[str, Any]:
    """Load metadata from .pkl, .joblib, or .json with robust fallback."""
    candidate_names = [
        "model_metadata.pkl",
        "model_metadata.joblib",
        "model_metadata.json",
    ]

    attempted_errors: list[str] = []

    for filename in candidate_names:
        metadata_path = _artifact_path(filename)
        if not metadata_path.exists():
            continue

        try:
            return _load_metadata_file(metadata_path)
        except Exception as exc:
            attempted_errors.append(f"{filename}: {exc}")

    if attempted_errors:
        raise MLServiceError(
            "No valid metadata file could be loaded. Tried: " + " | ".join(attempted_errors)
        )

    return _default_metadata()


def load_artifacts() -> tuple[Any, Any, dict[str, Any]]:
    """Load the model, degree encoder, and metadata only once per process."""
    global _MODEL_CACHE
    if _MODEL_CACHE:
        return _MODEL_CACHE["model"], _MODEL_CACHE["degree_encoder"], _MODEL_CACHE["metadata"]

    model_path = _first_existing_file([
        "student_stress_model.pkl",
        "student_stress_model.joblib",
    ])
    degree_encoder_path = _first_existing_file([
        "label_encoder_degree.pkl",
        "label_encoder_degree.joblib",
    ])

    missing = []
    if model_path is None:
        missing.append("student_stress_model.pkl")
    if degree_encoder_path is None:
        missing.append("label_encoder_degree.pkl")

    if missing:
        raise MLServiceError(
            "Missing ML artifact(s): "
            + ", ".join(missing)
            + ". Place your friend's files inside model_artifacts/."
        )

    metadata = _load_metadata()

    try:
        model = joblib.load(model_path)
        degree_encoder = joblib.load(degree_encoder_path)
    except Exception as exc:
        raise MLServiceError(f"Unable to load ML artifacts: {exc}") from exc

    _MODEL_CACHE = {
        "model": model,
        "degree_encoder": degree_encoder,
        "metadata": metadata,
    }
    return model, degree_encoder, metadata


def get_degree_choices() -> list[tuple[str, str]]:
    """Return degree choices from label_encoder_degree.pkl when available."""
    degree_encoder_path = _first_existing_file([
        "label_encoder_degree.pkl",
        "label_encoder_degree.joblib",
    ])

    if degree_encoder_path is not None:
        try:
            encoder = joblib.load(degree_encoder_path)
            if hasattr(encoder, "classes_"):
                return [(str(value), str(value)) for value in encoder.classes_]
        except Exception:
            pass

    return [(value, value) for value in FALLBACK_DEGREE_CHOICES]


def _clean_number(value: Any, default: float = 0.0) -> float:
    """Convert a form value into a finite float."""
    try:
        number = float(value)
        if not math.isfinite(number):
            return default
        return number
    except (TypeError, ValueError):
        return default


def _clean_int(value: Any, default: int = 0) -> int:
    """Convert a form value into an integer."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _metadata_features(metadata: dict[str, Any]) -> list[str]:
    """Read the feature order from metadata with a safe fallback."""
    features = metadata.get("features") or metadata.get("feature_names") or metadata.get("columns")
    if isinstance(features, list) and features:
        return [str(feature) for feature in features]
    return DEFAULT_FEATURE_ORDER


def _get_sleep_map(metadata: dict[str, Any]) -> dict[str, float]:
    """Return sleep duration mapping from metadata."""
    sleep_map = metadata.get("sleep_map") or DEFAULT_SLEEP_MAP
    return {str(key).strip("'"): float(value) for key, value in sleep_map.items()}


def _get_dietary_map(metadata: dict[str, Any]) -> dict[str, int]:
    """Return dietary habit mapping from metadata."""
    dietary_map = metadata.get("dietary_map") or DEFAULT_DIETARY_MAP
    return {str(key): int(value) for key, value in dietary_map.items()}


def _encode_degree(value: str, degree_encoder: Any) -> int:
    """Encode the user's degree with the same encoder used during training."""
    if not value:
        raise MLServiceError("Degree is required.")

    if not hasattr(degree_encoder, "transform"):
        raise MLServiceError("label_encoder_degree.pkl does not provide a transform() method.")

    try:
        return int(degree_encoder.transform([value])[0])
    except Exception as exc:
        allowed = [str(item) for item in getattr(degree_encoder, "classes_", [])]
        raise MLServiceError(
            f"Unknown degree value: {value}. Allowed values from the encoder: {allowed}"
        ) from exc


def normalize_form_data(form_data: dict[str, Any], degree_encoder: Any, metadata: dict[str, Any]) -> dict[str, float]:
    """Convert Flask form data into the exact feature names expected by the model."""
    sleep_map = _get_sleep_map(metadata)
    dietary_map = _get_dietary_map(metadata)

    sleep_value = str(form_data.get("sleep_duration", "")).strip()
    dietary_value = str(form_data.get("dietary_habits", "")).strip()

    if sleep_value not in sleep_map:
        raise MLServiceError(f"Unknown sleep duration: {sleep_value}. Allowed values: {list(sleep_map.keys())}")
    if dietary_value not in dietary_map:
        raise MLServiceError(f"Unknown dietary habit: {dietary_value}. Allowed values: {list(dietary_map.keys())}")

    model_ready = {
        "Age": _clean_int(form_data.get("age")),
        "Gender Num": _clean_int(form_data.get("gender")),
        "Academic Pressure": _clean_int(form_data.get("academic_pressure")),
        "Work Pressure": _clean_int(form_data.get("work_pressure")),
        "CGPA": _clean_number(form_data.get("cgpa")),
        "Study Satisfaction": _clean_int(form_data.get("study_satisfaction")),
        "Job Satisfaction": _clean_int(form_data.get("job_satisfaction")),
        "Sleep Duration Num": sleep_map[sleep_value],
        "Dietary Habits Num": dietary_map[dietary_value],
        "Suicidal Thoughts": _clean_int(form_data.get("suicidal_thoughts")),
        "Work/Study Hours": _clean_number(form_data.get("work_study_hours")),
        "Financial Stress": _clean_int(form_data.get("financial_stress")),
        "Family History": _clean_int(form_data.get("family_history")),
        "Degree Num": _encode_degree(str(form_data.get("degree", "")).strip(), degree_encoder),
    }

    return model_ready


def _display_input_data(form_data: dict[str, Any], model_input: dict[str, float]) -> dict[str, Any]:
    """Store a readable profile while keeping model-ready values for traceability."""
    return {
        "Age": model_input["Age"],
        "Gender": "Male" if model_input["Gender Num"] == 1 else "Female",
        "Academic Pressure": model_input["Academic Pressure"],
        "Work Pressure": model_input["Work Pressure"],
        "CGPA": model_input["CGPA"],
        "Study Satisfaction": model_input["Study Satisfaction"],
        "Job Satisfaction": model_input["Job Satisfaction"],
        "Sleep Duration": form_data.get("sleep_duration"),
        "Sleep Duration Num": model_input["Sleep Duration Num"],
        "Dietary Habits": form_data.get("dietary_habits"),
        "Dietary Habits Num": model_input["Dietary Habits Num"],
        "Suicidal Thoughts": "Yes" if model_input["Suicidal Thoughts"] == 1 else "No",
        "Work/Study Hours": model_input["Work/Study Hours"],
        "Financial Stress": model_input["Financial Stress"],
        "Family History": "Yes" if model_input["Family History"] == 1 else "No",
        "Degree": form_data.get("degree"),
        "Degree Num": model_input["Degree Num"],
    }


def _label_for_class(raw_class: Any) -> str:
    """Convert binary class output into a clear user-facing label."""
    return BINARY_CLASS_LABELS.get(raw_class, BINARY_CLASS_LABELS.get(str(raw_class), str(raw_class)))


def _build_probability_dict(model: Any, processed_input: pd.DataFrame) -> dict[str, float]:
    """Return probability percentages for each class."""
    if not hasattr(model, "predict_proba"):
        return {}

    raw_probabilities = model.predict_proba(processed_input)[0]
    classes = list(getattr(model, "classes_", range(len(raw_probabilities))))

    return {
        _label_for_class(classes[index]): round(float(probability) * 100, 2)
        for index, probability in enumerate(raw_probabilities)
    }


def _calculate_depression_risk_score(probabilities: dict[str, float], predicted_class: str) -> float:
    """Use class-1 probability as the risk score when available."""
    for label, value in probabilities.items():
        if "possible depression" in label.lower() or "depression risk" in label.lower():
            return round(float(value), 1)

    return 100.0 if "possible" in predicted_class.lower() else 0.0


def _build_explanation(predicted_class: str, model_input: dict[str, float]) -> str:
    """Create a simple explanation using the strongest model-aligned signals."""
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
        return (
            f"The model classified this profile as: {predicted_class}. "
            f"The main signals in the submitted form are {', '.join(reasons[:5])}."
        )

    return (
        f"The model classified this profile as: {predicted_class}. "
        "The submitted values do not show strong risk signals, but this result is still only a screening estimate."
    )


def predict_stress_level(form_data: dict[str, Any]) -> dict[str, Any]:
    """Preprocess form data, run the ML model, and return prediction outputs."""
    model, degree_encoder, metadata = load_artifacts()
    feature_order = _metadata_features(metadata)
    model_input = normalize_form_data(form_data, degree_encoder, metadata)

    missing_features = [feature for feature in feature_order if feature not in model_input]
    if missing_features:
        raise MLServiceError(f"The form does not provide required model feature(s): {missing_features}")

    processed_input = pd.DataFrame([model_input], columns=feature_order)

    try:
        raw_prediction = model.predict(processed_input)[0]
    except Exception as exc:
        raise MLServiceError(
            "Prediction failed. Check that the form fields, feature order, and encoders match the training pipeline: "
            f"{exc}"
        ) from exc

    predicted_class = _label_for_class(raw_prediction)
    probabilities = _build_probability_dict(model, processed_input)

    if not probabilities:
        probabilities = {
            "No depression risk detected": 0.0,
            "Possible depression risk": 0.0,
        }
        probabilities[predicted_class] = 100.0

    overall_score = _calculate_depression_risk_score(probabilities, predicted_class)
    explanation = _build_explanation(predicted_class, model_input)

    return {
        "predicted_class": predicted_class,
        "probabilities": probabilities,
        "overall_score": overall_score,
        "explanation": explanation,
        "input_data": _display_input_data(form_data, model_input),
        "model_input": model_input,
        "feature_order": feature_order,
    }
