"""Specialist model."""

from datetime import datetime, timezone

from app.extensions import db


class Specialist(db.Model):
    """Mental health specialist, counselor, support center, or hotline."""

    __tablename__ = "specialists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    specialty = db.Column(db.String(160), nullable=False)
    contact = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<Specialist {self.name}>"
