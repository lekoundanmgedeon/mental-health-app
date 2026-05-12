# Student MindCare - Mental Health Screening Web App

Student MindCare is a professional Flask web application that uses a pretrained Machine Learning model to estimate whether a student profile indicates a possible depression risk. It includes authentication, a Bootstrap 5 dashboard, prediction history, dynamic recommendations, specialists management, SQLite storage, and model integration with `joblib`.

> Important: this application is an educational screening and decision-support tool. It is not a medical diagnosis system. If the user feels unsafe, reports suicidal thoughts, or is in immediate danger, they should contact emergency services or a qualified mental health professional immediately.

## Real model currently integrated

The application is aligned with your friend's model metadata:

```text
Model: RandomForestClassifier
Task: binary_classification
Target: Depression (0 = No, 1 = Yes)
```

Expected model artifacts:

```text
model_artifacts/student_stress_model.pkl
model_artifacts/label_encoder_degree.pkl
model_artifacts/model_metadata.pkl
```

The app also accepts fallback filenames:

```text
student_stress_model.joblib
label_encoder_degree.joblib
model_metadata.joblib
model_metadata.json
```

## Features used by the model

The Flask form is aligned with these 14 model features:

```text
Age
Gender Num
Academic Pressure
Work Pressure
CGPA
Study Satisfaction
Job Satisfaction
Sleep Duration Num
Dietary Habits Num
Suicidal Thoughts
Work/Study Hours
Financial Stress
Family History
Degree Num
```

The user-friendly form fields are converted as follows:

| Form field | Model feature |
|---|---|
| age | Age |
| gender | Gender Num |
| academic_pressure | Academic Pressure |
| work_pressure | Work Pressure |
| cgpa | CGPA |
| study_satisfaction | Study Satisfaction |
| job_satisfaction | Job Satisfaction |
| sleep_duration | Sleep Duration Num |
| dietary_habits | Dietary Habits Num |
| suicidal_thoughts | Suicidal Thoughts |
| work_study_hours | Work/Study Hours |
| financial_stress | Financial Stress |
| family_history | Family History |
| degree | Degree Num |

## Project structure

```bash
mental_health_app/
├── app.py
├── wsgi.py
├── config.py
├── requirements.txt
├── Procfile
├── README.md
├── .env.example
├── .gitignore
├── model_artifacts/
│   ├── README.md
│   ├── model_metadata.json
│   ├── student_stress_model.pkl          # add your real file here
│   ├── label_encoder_degree.pkl          # add your real file here
│   └── model_metadata.pkl                # add your real file here if available
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   │   ├── ml_service.py
│   │   └── recommendation_service.py
│   ├── forms/
│   │   └── prediction_forms.py
│   ├── templates/
│   └── static/
└── instance/
```

## Run locally

```bash
cd mental_health_app
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
python app.py
```

Open:

```txt
http://127.0.0.1:5000
```

The SQLite database is created automatically in `instance/mental_health.db` when the app starts.

## Add your real model files

Copy these files into `model_artifacts/`:

```bash
cp student_stress_model.pkl mental_health_app/model_artifacts/
cp label_encoder_degree.pkl mental_health_app/model_artifacts/
cp model_metadata.pkl mental_health_app/model_artifacts/
```

If your metadata is JSON instead of PKL, the app can also use:

```bash
model_artifacts/model_metadata.json
```

## Test the model artifacts

Run this from the project root:

```bash
python - <<'PY'
import joblib
from pathlib import Path

model_dir = Path('model_artifacts')
model = joblib.load(model_dir / 'student_stress_model.pkl')
degree_encoder = joblib.load(model_dir / 'label_encoder_degree.pkl')

print('Model:', type(model))
print('Degree classes:', degree_encoder.classes_)
print('Model classes:', getattr(model, 'classes_', None))
print('Has predict_proba:', hasattr(model, 'predict_proba'))
PY
```

## Deployment on Render

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Connect your GitHub repository.
4. Use these settings:

```txt
Build command: pip install -r requirements.txt
Start command: gunicorn wsgi:app
```

5. Add environment variables:

```txt
SECRET_KEY=your-production-secret-key
FLASK_DEBUG=0
```

## Deployment on Railway

1. Push the project to GitHub.
2. Create a new Railway project from GitHub.
3. Add environment variables:

```txt
SECRET_KEY=your-production-secret-key
FLASK_DEBUG=0
```

4. Railway uses the `Procfile`:

```txt
web: gunicorn wsgi:app
```

## Deployment on PythonAnywhere

1. Upload the project folder.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. In the PythonAnywhere Web tab, set the Flask app path to `wsgi.py`.
5. Add environment variables or edit `config.py` for your production secret key.

## Security notes

- Never commit a real `.env` file.
- Change `SECRET_KEY` in production.
- Do not expose user mental health data publicly.
- Use HTTPS in production.
- This app does not replace medical advice.

---

## Test ML predictions before opening the web interface

You can test the real model directly from the command line.

First, place the real artifacts in `model_artifacts/`:

```bash
model_artifacts/student_stress_model.pkl
model_artifacts/label_encoder_degree.pkl
model_artifacts/model_metadata.pkl
```

Then run:

```bash
python scripts/04_run_all_prediction_tests.py
```

Or run each script separately:

```bash
python scripts/01_inspect_model_artifacts.py
python scripts/02_test_single_prediction.py
python scripts/02_test_single_prediction.py --profile high_risk_student
python scripts/03_test_batch_predictions.py
```

The scripts generate:

```bash
outputs/single_prediction_result.json
outputs/batch_prediction_results.json
outputs/batch_prediction_results.csv
```

The test input profiles are stored here:

```bash
tests/test_inputs/sample_profiles.json
```

The sample profiles use the same form field names as the Flask form. The ML service converts them into the exact model features: `Age`, `Gender Num`, `Academic Pressure`, `Work Pressure`, `CGPA`, `Study Satisfaction`, `Job Satisfaction`, `Sleep Duration Num`, `Dietary Habits Num`, `Suicidal Thoughts`, `Work/Study Hours`, `Financial Stress`, `Family History`, and `Degree Num`.


## Model artifact compatibility

The real student stress model artifacts were trained with scikit-learn 1.6.1. Use `pip install --upgrade --force-reinstall scikit-learn==1.6.1` if you see an `InconsistentVersionWarning`.
# mental-health-app
