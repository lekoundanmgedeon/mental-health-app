# Command-line prediction tests

These tests let you validate the Machine Learning integration before opening the Flask web interface.

## Required files

Place your real artifacts here:

```bash
model_artifacts/student_stress_model.pkl
model_artifacts/label_encoder_degree.pkl
model_artifacts/model_metadata.pkl
```

The application also accepts `.joblib` files and `model_metadata.json`.

## Run all tests

```bash
python scripts/04_run_all_prediction_tests.py
```

## Run individual tests

```bash
python scripts/01_inspect_model_artifacts.py
python scripts/02_test_single_prediction.py
python scripts/02_test_single_prediction.py --profile high_risk_student
python scripts/03_test_batch_predictions.py
```

## Outputs

Generated files are saved in:

```bash
outputs/single_prediction_result.json
outputs/batch_prediction_results.json
outputs/batch_prediction_results.csv
```

## Input profiles

Edit this file to create more tests:

```bash
tests/test_inputs/sample_profiles.json
```

Use `"degree": "__AUTO_FIRST__"` if you want the script to automatically choose the first valid degree from `label_encoder_degree.pkl`.

## Important scikit-learn version note

The provided artifacts were trained with scikit-learn 1.6.1. If you see `InconsistentVersionWarning`, update the environment with:

```bash
pip install --upgrade --force-reinstall scikit-learn==1.6.1
```

Then run:

```bash
python scripts/00_check_environment.py
python scripts/01_inspect_model_artifacts.py
python scripts/04_run_all_prediction_tests.py
```
