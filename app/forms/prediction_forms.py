"""Prediction and specialist forms.

The prediction form is aligned with the real student depression model features
listed in model_metadata.json / model_metadata.pkl.
"""

from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional


class PredictionForm(FlaskForm):
    """Collect exactly the inputs required by the trained ML model."""

    age = IntegerField(
        "Age",
        validators=[InputRequired(), NumberRange(min=10, max=100)],
        render_kw={"placeholder": "Example: 22"},
    )

    gender = SelectField(
        "Gender",
        coerce=int,
        choices=[(0, "Female"), (1, "Male")],
        validators=[InputRequired()],
    )

    academic_pressure = SelectField(
        "Academic Pressure",
        coerce=int,
        choices=[
            (1, "1 - Very low"),
            (2, "2 - Low"),
            (3, "3 - Moderate"),
            (4, "4 - High"),
            (5, "5 - Very high"),
        ],
        validators=[InputRequired()],
    )

    work_pressure = SelectField(
        "Work Pressure",
        coerce=int,
        choices=[
            (0, "0 - Not applicable / no work"),
            (1, "1 - Very low"),
            (2, "2 - Low"),
            (3, "3 - Moderate"),
            (4, "4 - High"),
            (5, "5 - Very high"),
        ],
        validators=[InputRequired()],
    )

    cgpa = FloatField(
        "CGPA / Average grade",
        validators=[InputRequired(), NumberRange(min=0, max=10)],
        render_kw={"placeholder": "Example: 7.8", "step": "0.01"},
    )

    study_satisfaction = SelectField(
        "Study Satisfaction",
        coerce=int,
        choices=[
            (1, "1 - Very dissatisfied"),
            (2, "2 - Dissatisfied"),
            (3, "3 - Neutral"),
            (4, "4 - Satisfied"),
            (5, "5 - Very satisfied"),
        ],
        validators=[InputRequired()],
    )

    job_satisfaction = SelectField(
        "Job Satisfaction",
        coerce=int,
        choices=[
            (0, "0 - Not applicable / no job"),
            (1, "1 - Very dissatisfied"),
            (2, "2 - Dissatisfied"),
            (3, "3 - Neutral"),
            (4, "4 - Satisfied"),
            (5, "5 - Very satisfied"),
        ],
        validators=[InputRequired()],
    )

    sleep_duration = SelectField(
        "Sleep Duration",
        choices=[
            ("Less than 5 hours", "Less than 5 hours"),
            ("5-6 hours", "5-6 hours"),
            ("6-7 hours", "6-7 hours"),
            ("7-8 hours", "7-8 hours"),
            ("More than 8 hours", "More than 8 hours"),
        ],
        validators=[InputRequired()],
    )

    dietary_habits = SelectField(
        "Dietary Habits",
        choices=[
            ("Unhealthy", "Unhealthy"),
            ("Moderate", "Moderate"),
            ("Healthy", "Healthy"),
        ],
        validators=[InputRequired()],
    )

    suicidal_thoughts = SelectField(
        "Have you ever had suicidal thoughts?",
        coerce=int,
        choices=[(0, "No"), (1, "Yes")],
        validators=[InputRequired()],
    )

    work_study_hours = FloatField(
        "Work/Study Hours per day",
        validators=[InputRequired(), NumberRange(min=0, max=24)],
        render_kw={"placeholder": "Example: 8", "step": "0.5"},
    )

    financial_stress = SelectField(
        "Financial Stress",
        coerce=int,
        choices=[
            (1, "1 - Very low"),
            (2, "2 - Low"),
            (3, "3 - Moderate"),
            (4, "4 - High"),
            (5, "5 - Very high"),
        ],
        validators=[InputRequired()],
    )

    family_history = SelectField(
        "Family History of Mental Illness",
        coerce=int,
        choices=[(0, "No"), (1, "Yes")],
        validators=[InputRequired()],
    )

    # Choices are dynamically replaced in prediction_routes.py from label_encoder_degree.pkl.
    degree = SelectField(
        "Degree",
        choices=[],
        validators=[InputRequired()],
    )

    submit = SubmitField("Analyze mental health risk")


class SpecialistForm(FlaskForm):
    """Create or update a specialist card."""

    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=160)])
    specialty = StringField("Specialty", validators=[DataRequired(), Length(min=2, max=160)])
    contact = StringField("Contact", validators=[DataRequired(), Length(min=2, max=160)])
    location = StringField("Location", validators=[DataRequired(), Length(min=2, max=160)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save")
