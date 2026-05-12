"""Prediction model."""

import json
from datetime import datetime, timezone

from app.extensions import db


class Prediction(db.Model):
    """Stores each prediction made by a user."""

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    input_data = db.Column(db.Text, nullable=False)
    predicted_class = db.Column(db.String(80), nullable=False)
    probabilities = db.Column(db.Text, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    recommendation_summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="predictions")

    @property
    def input_json(self) -> dict:
        """Return input_data as a dictionary."""
        return json.loads(self.input_data or "{}")

    @property
    def probability_json(self) -> dict:
        """Return probabilities as a dictionary."""
        return json.loads(self.probabilities or "{}")

    def __repr__(self) -> str:
        return f"<Prediction {self.predicted_class} for user {self.user_id}>"
