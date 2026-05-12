"""Prediction routes."""

import json

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.prediction_forms import PredictionForm
from app.models.prediction import Prediction
from app.services.ml_service import MLServiceError, get_degree_choices, predict_stress_level
from app.services.recommendation_service import build_recommendations

prediction_bp = Blueprint("prediction", __name__, url_prefix="/prediction")


@prediction_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_prediction():
    """Display and process the prediction form."""
    form = PredictionForm()
    form.degree.choices = get_degree_choices()
    if form.validate_on_submit():
        try:
            result = predict_stress_level(form.data)
            recommendations = build_recommendations(result["predicted_class"], result["input_data"])
        except MLServiceError as exc:
            flash(str(exc), "danger")
            return render_template("prediction/form.html", form=form, title="New prediction")

        prediction = Prediction(
            user_id=current_user.id,
            input_data=json.dumps(result["input_data"]),
            predicted_class=result["predicted_class"],
            probabilities=json.dumps(result["probabilities"]),
            overall_score=result["overall_score"],
            recommendation_summary=recommendations["summary"],
        )
        db.session.add(prediction)
        db.session.commit()

        flash("Prediction completed successfully.", "success")
        return redirect(url_for("prediction.result", prediction_id=prediction.id))

    return render_template("prediction/form.html", form=form, title="New prediction")


@prediction_bp.route("/result/<int:prediction_id>")
@login_required
def result(prediction_id: int):
    """Display a saved prediction result."""
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    input_data = prediction.input_json
    probabilities = prediction.probability_json
    recommendations = build_recommendations(prediction.predicted_class, input_data)
    explanation = result_explanation(prediction.predicted_class, input_data)
    return render_template(
        "prediction/result.html",
        title="Prediction result",
        prediction=prediction,
        input_data=input_data,
        probabilities=probabilities,
        recommendations=recommendations,
        explanation=explanation,
    )


@prediction_bp.route("/history")
@login_required
def history():
    """Show prediction history for the current user."""
    predictions = (
        Prediction.query.filter_by(user_id=current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return render_template("prediction/history.html", title="Prediction history", predictions=predictions)


def result_explanation(predicted_class: str, input_data: dict[str, float]) -> str:
    """Build a simple explanation when reading a saved result."""
    signals = []

    if input_data.get("Suicidal Thoughts") == "Yes":
        signals.append("reported suicidal thoughts")
    if float(input_data.get("Academic Pressure", 0)) >= 4:
        signals.append("high academic pressure")
    if float(input_data.get("Financial Stress", 0)) >= 4:
        signals.append("high financial stress")
    if float(input_data.get("Work/Study Hours", 0)) >= 9:
        signals.append("long work/study hours")
    if float(input_data.get("Sleep Duration Num", 8)) < 6:
        signals.append("short sleep duration")
    if float(input_data.get("Study Satisfaction", 5)) <= 2:
        signals.append("low study satisfaction")
    if input_data.get("Family History") == "Yes":
        signals.append("family history of mental illness")

    if signals:
        return f"This result is mainly associated with {', '.join(signals[:5])}."
    return f"This result indicates {predicted_class} based on the submitted student profile."
