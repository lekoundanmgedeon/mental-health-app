"""Specialist seeding and helper functions."""

from app.extensions import db
from app.models.specialist import Specialist


DEFAULT_SPECIALISTS = [
    {
        "name": "University Student Counseling Center",
        "specialty": "Student mental health support",
        "contact": "support@example.edu",
        "location": "Campus health center",
        "description": "First contact point for academic stress, anxiety, and wellbeing guidance.",
    },
    {
        "name": "Dr. Amina Diallo",
        "specialty": "Clinical psychologist",
        "contact": "+221 00 000 00 00",
        "location": "Dakar / Online",
        "description": "Psychological support for stress, burnout, and student life balance.",
    },
    {
        "name": "Student Success Coach",
        "specialty": "Academic coaching",
        "contact": "coach@example.com",
        "location": "Online",
        "description": "Time management, revision planning, workload organization, and exam preparation.",
    },
    {
        "name": "Emergency Support Hotline",
        "specialty": "Urgent support service",
        "contact": "Local emergency number",
        "location": "Available locally",
        "description": "Use this contact immediately if the student feels unsafe or in crisis.",
    },
]


def seed_default_specialists() -> None:
    """Seed starter specialists if the table is empty."""
    if Specialist.query.first():
        return
    for item in DEFAULT_SPECIALISTS:
        db.session.add(Specialist(**item))
    db.session.commit()
