# Generate-Plan: Research-Backed Implementation Plan (ML Heart Prediction)

Based on `examples/ml_heart_prediction/initial-prompt-template_heart.md`.

## 1) Core Principles & Success Criteria
- **Primary goal**: Build a supervised binary classifier on synthetic data with calibrated probabilities suitable for screening.
- **Success criteria** (prompt lines 106–109):
  - ROC AUC ≥ 0.80; PR AUC ≥ 0.35 on test.
  - Recall ≥ 0.70 at precision ≥ 0.60 after threshold tuning.
  - End-to-end, reproducible run with artifacts in `output/`.

## 2) System Architecture & File Structure
- **Proposed structure**:
  - `examples/ml_heart_prediction/`
    - `generate_data.py` (synthetic dataset via `make_classification`)
    - `pipeline.py` (sklearn/imblearn Pipelines with scaling + SMOTE + model)
    - `train_eval.py` (Stratified splits, CV, GridSearchCV, threshold tuning)
    - `calibration.py` (CalibratedClassifierCV: isotonic)
    - `metrics.py` (ROC/PR AUC, confusion, precision-recall curve)
    - `importance.py` (coef_ and permutation importance)
    - `plots.py` (ROC/PR plots)
    - `save_artifacts.py` (save best model, metrics, plots to `output/`)
    - `run.py` (orchestrates E2E)
    - `config.py` (seeds, CV params, paths, model grids)
    - `output/` (artifacts)

## 3) Research-Backed Methods and Rationale
- **Imbalance handling & leakage control**:
  - Use `imblearn.pipeline.Pipeline` to place SMOTE and scaling inside CV folds to avoid leakage [imblearn Pipeline docs].
    - https://imbalanced-learn.org/stable/references/generated/imblearn.pipeline.Pipeline.html
  - SMOTE for minority oversampling (compare vs class_weight) [SMOTE docs].
    - https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html
- **Calibration**:
  - Apply `CalibratedClassifierCV` with isotonic for better probability calibration [sklearn 1.7.1].
    - Overview: https://scikit-learn.org/stable/modules/calibration.html
    - API: https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html
- **Validation**:
  - Use `StratifiedKFold` for consistent class ratios across splits [sklearn 1.7.1].
    - https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html
- **Threshold tuning**:
  - Use `precision_recall_curve` to select threshold meeting recall/precision targets [sklearn 1.7.1].
    - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html
- **Explainability**:
  - Coefficients for linear models; permutation importance for tree-based [sklearn 1.7.1].
    - https://scikit-learn.org/stable/modules/permutation_importance.html
- **Clinical reporting standard**:
  - Align with TRIPOD+AI 27-item checklist (BMJ 2024) for ML predictions.
    - https://www.bmj.com/content/385/bmj-2023-078378

## 4) Detailed Task Breakdown (Sequential)
- **Task 1: Setup**
  - Create `config.py` with seeds, CV params (StratifiedKFold n_splits=5), paths.
  - Create folder `output/` (if missing).
- **Task 2: Data generation**
  - Implement `generate_data.py` using `make_classification` with prompt specs (5k rows, ~15% positive).
- **Task 3: Pipelines**
  - `pipeline.py`:
    - Baselines: LogisticRegression + StandardScaler; RandomForestClassifier; optional GradientBoosting.
    - Variant A: class_weight approach (no SMOTE).
    - Variant B: imblearn Pipeline: StandardScaler (if needed) → SMOTE → model.
- **Task 4: CV + model selection**
  - `train_eval.py`:
    - Stratified train/val/test split (fixed seeds).
    - GridSearchCV over model-specific grids; primary metric ROC AUC; log PR AUC, F1, etc.
- **Task 5: Calibration**
  - `calibration.py`: Fit `CalibratedClassifierCV` (method="isotonic").
- **Task 6: Threshold tuning**
  - Use `precision_recall_curve` on validation predictions to select threshold achieving recall ≥ 0.70 with precision ≥ 0.60; evaluate on test.
- **Task 7: Explainability**
  - `importance.py`: coefficients (linear) and permutation importance (tree-based) on held-out set.
- **Task 8: Plots & metrics**
  - `plots.py`: ROC and PR curves; `metrics.py`: confusion matrix and summary metrics at chosen threshold.
- **Task 9: Artifact export**
  - `save_artifacts.py`: Save best model, calibrated model, metrics report (JSON/CSV), plots to `output/`.
- **Task 10: TRIPOD+AI documentation**
  - Brief results note aligned to TRIPOD+AI (data generation, validation, calibration, thresholds, reproducibility items).
- **Task 11: Orchestration**
  - `run.py`: Wire the steps E2E with fixed seeds and logging.

## 5) Acceptance Tests
- **Data**: Class balance ~15% positive; feature counts as specified.
- **CV**: Stratification preserved across folds.
- **Leakage**: All preprocessing and SMOTE inside Pipeline used within CV; no fit on test.
- **Performance**: Test ROC AUC ≥ 0.80; PR AUC ≥ 0.35.
- **Threshold**: Recall ≥ 0.70 at precision ≥ 0.60 on validation; confirm on test.
- **Calibration**: Reliability curve improves after isotonic calibration.
- **Artifacts**: `output/` contains best model, calibrated model, metrics, ROC/PR plots.
- **Reproducibility**: Fixed seeds; deterministic results within tolerance.

## 6) Risks & Mitigations
- **Overfitting during calibration**: Use split-based calibration; never calibrate on test.
- **SMOTE misuse**: Ensure SMOTE occurs inside CV folds via imblearn Pipeline to prevent leakage.
- **Runtime**: Restrict grid sizes; cap trees/depth; set `n_jobs` to meet <60s target.

## 7) Runtime and Resource Target
- Single CPU laptop; target <60 seconds. Start with tight grids; expand only if criteria not met.

## 8) Execution Route After Approval
- After plan approval: proceed to `/tripod-ml-pipeline` for ML execution with the above design, ensuring TRIPOD+AI items are documented.

## Verified References
- imblearn Pipeline: https://imbalanced-learn.org/stable/references/generated/imblearn.pipeline.Pipeline.html
- SMOTE: https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html
- Calibration overview: https://scikit-learn.org/stable/modules/calibration.html
- CalibratedClassifierCV: https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html
- StratifiedKFold: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html
- precision_recall_curve: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html
- Permutation importance: https://scikit-learn.org/stable/modules/permutation_importance.html
- TRIPOD+AI (BMJ): https://www.bmj.com/content/385/bmj-2023-078378

## Phased, Checklist-Driven Plan

Success targets: ROC AUC ≥ 0.80; PR AUC ≥ 0.35; recall ≥ 0.70 at precision ≥ 0.60; full reproducibility.

### Phase 0 — Governance & Environment
- [ ] Confirm repo state; avoid destructive ops without explicit approval
- [ ] Create and activate venv; install `requirements.txt`
- [ ] Set deterministic seeds in `config.py`
- [ ] Ensure `examples/ml_heart_prediction/output/` exists
- [ ] Sanity run `run.py` to verify scaffold

Deliverables:
- [ ] `output/` present
- [ ] Sanity run output captured

Exit criteria:
- [ ] Environment reproducible and scaffold runnable

### Phase 1 — Synthetic Data Generation + Documentation
- [ ] Implement `generate_data.py` with `sklearn.datasets.make_classification`
  - [ ] 5,000 samples, 13 features (configurable), ~15% positive class
  - [ ] Fixed `random_state` from `config.py`
- [ ] Stratified train/val/test split (e.g., 70/15/15) using `StratifiedShuffleSplit`
- [ ] Save dataset snapshot to `output/` (csv/parquet + schema summary)
- [ ] Document generation parameters and rationale (TRIPOD+AI data section)

Deliverables:
- [ ] `output/data_summary.json`
- [ ] `output/dataset_head.csv` (optional)
- [ ] TRIPOD+AI data documentation note

Exit criteria:
- [ ] Correct class balance and feature schema confirmed

### Phase 2 — EDA + Baseline Metrics
- [ ] Minimal EDA (`data_analysis.py` or inside `train_eval.py`)
  - [ ] Class distribution, missing checks, feature scales
- [ ] Baseline model: `DummyClassifier ("stratified")`
- [ ] Evaluate ROC AUC, PR AUC on validation
- [ ] Save plots and baseline metrics

Deliverables:
- [ ] `output/eda_report.json`
- [ ] `output/baseline_metrics.json`
- [ ] `output/plots/baseline_pr_roc.png`

Exit criteria:
- [ ] Baseline established; data issues ruled out

### Phase 3 — Modeling Pipelines + Imbalance Strategy
- [ ] Implement `pipeline.py` with `imblearn.pipeline.Pipeline`
  - [ ] Variant A: LogisticRegression + StandardScaler (+ class_weight)
  - [ ] Variant B: LogisticRegression + StandardScaler + SMOTE
  - [ ] Variant C: RandomForestClassifier (+ class_weight) vs SMOTE variant
- [ ] Ensure SMOTE/scaling reside inside CV pipeline to prevent leakage
- [ ] Define tight, CPU-friendly grids in `config.py`

Deliverables:
- [ ] `pipeline.py` with pipelines registered
- [ ] `config.py` hyperparameter grids

Exit criteria:
- [ ] Pipelines compile and can fit in CV

### Phase 4 — Cross-Validation + Model Selection
- [ ] Use `StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)`
- [ ] `GridSearchCV` (primary: ROC AUC), also log PR AUC, F1
- [ ] Compare class_weight vs SMOTE variants
- [ ] Select best model by ROC AUC; capture mean ± std

Deliverables:
- [ ] `output/cv_results.csv`
- [ ] `output/best_model_cv_summary.json`

Exit criteria:
- [ ] Best pipeline identified with stable CV performance

### Phase 5 — Probability Calibration
- [ ] Apply `CalibratedClassifierCV(method="isotonic")` to best estimator
  - [ ] Calibrate using CV or validation only (never test)
- [ ] Plot reliability curves pre/post calibration
- [ ] Save calibrated estimator

Deliverables:
- [ ] `output/calibration_summary.json`
- [ ] `output/plots/reliability_pre_post.png`
- [ ] `output/models/best_calibrated.joblib`

Exit criteria:
- [ ] Improved calibration demonstrated without overfitting

### Phase 6 — Threshold Tuning (Validation-Driven)
- [ ] Use `precision_recall_curve` on validation predictions
- [ ] Choose threshold meeting recall ≥ 0.70 at precision ≥ 0.60
- [ ] Freeze threshold; evaluate on test

Deliverables:
- [ ] `output/threshold_selection.json` (threshold grid + selected)
- [ ] `output/plots/precision_recall_thresholds.png`

Exit criteria:
- [ ] Threshold locked and justified

### Phase 7 — Final Evaluation on Test
- [ ] Evaluate ROC AUC, PR AUC on test
- [ ] Apply chosen threshold: confusion matrix, precision, recall, F1
- [ ] Compare against success criteria

Deliverables:
- [ ] `output/final_test_metrics.json`
- [ ] `output/plots/final_roc_pr.png`

Exit criteria:
- [ ] Targets met (ROC AUC ≥ 0.80; PR AUC ≥ 0.35)

### Phase 8 — Explainability
- [ ] LogisticRegression: standardized coefficients and odds interpretation
- [ ] Tree-based: permutation importance on hold-out set
- [ ] Summarize key features influencing predictions

Deliverables:
- [ ] `output/importance_report.json`
- [ ] `output/plots/feature_importance.png`

Exit criteria:
- [ ] Explainability suitable for clinical discussion

### Phase 9 — Artifacts & Reproducibility
- [ ] Persist artifacts: models, metrics, CV tables, threshold selection, plots
- [ ] Save `output/run_manifest.json` (versions, seeds, hashes, config)
- [ ] Document run steps in example `README.md`

Deliverables:
- [ ] Complete, re-runnable artifact set

Exit criteria:
- [ ] One-command reproducible run

### Phase 10 — TRIPOD+AI Documentation
- [ ] Populate items: data (synthetic), predictors, outcome, sample size, missing data
- [ ] Model development, validation, calibration, thresholding
- [ ] Performance measures, uncertainty, limitations
- [ ] Export compliance checklist and short results report

Deliverables:
- [ ] `docs/tripod_compliance/checklist.md`
- [ ] `docs/tripod_compliance/results_summary.md`

Exit criteria:
- [ ] Compliance items documented and linked to artifacts

### Phase 11 — Orchestration Integration
- [ ] Implement `run.py` orchestration: Data → EDA → Pipelines → CV → Calibration → Threshold → Test → Explainability → Save → Docs hooks
- [ ] Add structured logging and timing
- [ ] Final smoke test end-to-end

Deliverables:
- [ ] `examples/ml_heart_prediction/run.py` produces all artifacts
- [ ] `output/` updated with fresh run artifacts

Exit criteria:
- [ ] Single command produces all deliverables deterministically

### Global Gates and Guards
- [ ] No preprocessing/SMOTE outside CV folds
- [ ] No calibration or threshold search on test
- [ ] Fixed seeds across randomized components
- [ ] If targets not met, loop back to Phase 3 with restricted grid expansion

### Approval Checkpoint
- Approval required to proceed with `/tripod-ml-pipeline` execution per this phased plan.
