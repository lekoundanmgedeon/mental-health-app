"""Landing and dashboard routes."""

from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from app.models.prediction import Prediction

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def landing():
    """Public landing page."""
    return render_template("landing.html", title="Student MindCare")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Authenticated user dashboard."""
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    last_prediction = (
        Prediction.query.filter_by(user_id=current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    avg_score = (
        Prediction.query.with_entities(func.avg(Prediction.overall_score))
        .filter_by(user_id=current_user.id)
        .scalar()
    )
    recent_predictions = (
        Prediction.query.filter_by(user_id=current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        title="Dashboard",
        total_predictions=total_predictions,
        last_prediction=last_prediction,
        avg_score=round(avg_score or 0, 1),
        recent_predictions=recent_predictions,
    )
