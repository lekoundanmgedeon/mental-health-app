"""Dynamic recommendations based on depression-risk prediction outputs."""

from __future__ import annotations


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_recommendations(predicted_class: str, input_data: dict[str, object]) -> dict[str, object]:
    """Return personalized recommendations for the result page.

    This app is a screening and educational support tool, not a diagnosis tool.
    """
    recommendations: list[str] = []
    predicted_lower = predicted_class.lower()

    if "possible depression" in predicted_lower or "risk" in predicted_lower and "no" not in predicted_lower:
        recommendations.extend([
            "Consider speaking with a counselor, psychologist, student support service, or trusted healthcare professional.",
            "Reduce overload where possible and create a simple recovery plan for the next 24 to 48 hours.",
            "Do not rely on the app result as a diagnosis; use it as a signal to seek appropriate support.",
        ])
    else:
        recommendations.extend([
            "Maintain healthy routines and continue monitoring your academic and personal workload.",
            "Keep regular sleep, meals, breaks, and social contact to protect your wellbeing.",
            "Repeat the screening later if your situation changes significantly.",
        ])

    if input_data.get("Suicidal Thoughts") == "Yes":
        recommendations.insert(
            0,
            "Because suicidal thoughts were reported, contact a qualified professional, a crisis line, or emergency services immediately if there is any immediate danger.",
        )

    if _to_float(input_data.get("Academic Pressure")) >= 4:
        recommendations.append("Academic pressure is high. Break tasks into smaller priorities and speak with a teacher, tutor, or academic advisor.")

    if _to_float(input_data.get("Financial Stress")) >= 4:
        recommendations.append("Financial stress is high. Consider contacting student financial aid, social services, or a campus support office.")

    if _to_float(input_data.get("Work/Study Hours")) >= 9:
        recommendations.append("Your work/study hours are very high. Add recovery blocks and avoid long uninterrupted sessions.")

    if _to_float(input_data.get("Sleep Duration Num"), 8) < 6:
        recommendations.append("Sleep duration is low. Try to protect a stable sleep window and reduce late-night screen exposure.")

    if _to_float(input_data.get("Study Satisfaction"), 5) <= 2:
        recommendations.append("Study satisfaction is low. Review what is blocking your progress and ask for academic guidance early.")

    if _to_float(input_data.get("Dietary Habits Num"), 3) <= 1:
        recommendations.append("Dietary habits are marked unhealthy. Try to add regular meals and hydration during study days.")

    if input_data.get("Family History") == "Yes":
        recommendations.append("Family history was reported. Monitoring symptoms and speaking with a professional may be especially useful.")

    # Remove duplicates while preserving order.
    unique_recommendations = list(dict.fromkeys(recommendations))

    return {
        "summary": unique_recommendations[0] if unique_recommendations else "Keep monitoring your wellbeing.",
        "items": unique_recommendations,
    }
