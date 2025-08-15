# ML Heart Prediction Example

A minimal, approval-gated ML/AI workflow demo that shows how to run a research-backed pipeline with TRIPOD+AI documentation using this repository.

- Folder: `examples/ml_heart_prediction/`
- Entry point (scaffold): `run.py`
- Repo plan: `plans/ml_heart_prediction_plan.md`
- Output dir: `examples/ml_heart_prediction/output/`

## What This Example Demonstrates
- Research-first planning with user approval before execution
- Leakage-safe pipelines using `imblearn.Pipeline` (SMOTE inside CV)
- Probability calibration (`CalibratedClassifierCV`, isotonic)
- Threshold tuning on validation (never on test)
- TRIPOD+AI-aligned documentation and artifacts

## Two Ways to Drive It

### Option A: Workflow Slash-Commands (Recommended)
Use the repo’s built-in workflows from the root of the repository.

1) `/init-ml-context`
   - Detects ML signals and prepares TRIPOD+AI scaffolding
2) `/generate-plan` (approval gate)
   - Produces research-backed plan (see `plans/ml_heart_prediction_plan.md`)
3) `/tripod-ml-pipeline`
   - Executes the approved plan end-to-end with calibration and thresholding
4) `/validate-result`
   - Verifies acceptance criteria and summarizes results

Notes:
- These workflows operate repository-wide. This example folder provides a concrete instance to explore.

### Option B: Minimal Python Drive (Scaffold + Later Full Run)
From the repository root:

```bash
# Create venv, install requirements (if not already done)
# python -m venv .venv
# .venv\Scripts\activate  (Windows PowerShell)
# pip install -r requirements.txt

# Run the scaffold (just verifies the example wiring)
python examples/ml_heart_prediction/run.py
```

After the plan is approved and pipeline components are implemented (per `plans/ml_heart_prediction_plan.md`), this example will:
- Generate synthetic data
- Train and select models via stratified CV
- Calibrate probabilities
- Tune decision threshold on validation
- Evaluate on test and export artifacts to `output/`

## Files & Structure
- `run.py`: Entry point that ensures `output/` exists and prints scaffold status
- `config.py`: Central place to set output path and, later, seeds/params
- `output/`: Artifacts directory (created automatically)
- Planned modules (added during execution phases):
  - `generate_data.py` — synthetic data via `make_classification`
  - `pipeline.py` — imblearn pipelines (scaling/SMOTE/model)
  - `train_eval.py` — CV + model selection
  - `calibration.py` — isotonic calibration wrapper
  - `metrics.py`, `plots.py`, `importance.py`, `save_artifacts.py`

See the phased checklist in `plans/ml_heart_prediction_plan.md` for exact steps and exit criteria.

## Acceptance Criteria (for the full run)
- ROC AUC ≥ 0.80; PR AUC ≥ 0.35 on test
- Recall ≥ 0.70 at precision ≥ 0.60 after threshold tuning
- Full reproducibility (fixed seeds) and audit-ready artifacts

## Guardrails (Important)
- Do not fit preprocessing or SMOTE outside CV folds
- Do not calibrate or tune thresholds on test
- Keep seeds fixed for deterministic results

## Expected Artifacts (when fully executed)
- `output/models/best_calibrated.joblib`
- `output/cv_results.csv`, `final_test_metrics.json`, `threshold_selection.json`
- `output/plots/` — ROC, PR, reliability, and importance plots
- TRIPOD+AI docs under `docs/tripod_compliance/` (repo-level)

## Troubleshooting
- If `run.py` prints scaffold readiness but you see no artifacts, that’s expected before pipeline execution.
- Confirm you’re running from repo root when using relative paths.
- For Windows PowerShell, activate venv with: `.venv\Scripts\Activate.ps1`.

## Next Step
- Review `plans/ml_heart_prediction_plan.md` and approve the phased plan.
- Then run `/tripod-ml-pipeline` to execute the end-to-end workflow.
