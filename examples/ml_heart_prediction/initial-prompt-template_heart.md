# Project Prompt Template
<!-- 
  This is your project brief template. Copy this file and fill it out to define WHAT you want to build.
  The AI will use this to create a comprehensive step-by-step implementation plan.
-->

## 1. High-Level Goal
<!-- 
  **Your Goal:** In one or two sentences, describe the main objective of the project.
  **Example:** "I want to build a web app that converts currency using a public API."
-->

Build a supervised ML pipeline to predict likelihood of diabetes (binary classification) from 15 patient variables using synthetic data for development. Deliver reproducible training, stratified evaluation, and calibrated probability outputs suitable for screening workflows.

## 2. Core Features & Requirements
<!-- 
  **Your Goal:** List the essential features as a bulleted list. Be specific and detailed.
  **Example:**
  - Must have a dropdown to select the 'from' and 'to' currencies
  - Must have an input box for the amount
  - Must display the converted amount clearly
  - Must show the last updated time for the exchange rate
-->

- Synthetic dataset generation: 5,000 rows, 15 features (e.g., 6 informative, 4 redundant, 5 noise) via `sklearn.datasets.make_classification` with ~15% positive class to mimic class imbalance.
- Data splitting and validation: stratified train/validation/test split plus 5-fold Stratified CV on the train set.
- Models: baseline `LogisticRegression` (with `class_weight='balanced'`) and `RandomForestClassifier`; optional `GradientBoostingClassifier`.
- Imbalance handling: compare class weights vs. `imblearn` SMOTE inside a `Pipeline` to avoid data leakage.
- Preprocessing: `StandardScaler` for linear models inside the same `Pipeline`.
- Metrics: primary ROC AUC; also PR AUC, F1, recall at fixed precision, confusion matrix; plot ROC and PR curves.
- Model selection: `GridSearchCV` with stratified CV and consistent `random_state` for reproducibility.
- Explainability: feature importance (`coef_` for linear, permutation importance for tree-based models).
- Artifacts: save best model, metrics report, and evaluation plots to an `output/` folder.

## 3. Technology Stack
<!-- 
  **Your Goal:** List the programming languages, libraries, and frameworks you want to use.
  **Example:**
  - Language: JavaScript
  - Framework: React
  - Libraries: axios, Material-UI
  - Database: PostgreSQL
-->

- Language: Python 3.12
- Framework: None (scikit-learn pipelines)
- Libraries: scikit-learn, imbalanced-learn, pandas, numpy, matplotlib, seaborn
- Database: None (in-memory synthetic data; optional CSV export)

## 4. Code Examples
<!-- 
  **Your Goal:** (Optional but powerful) If you have specific code patterns or styles, 
  create files in the `examples/` folder and reference them here.
  **Example:** "See `examples/my-api-handler.js` for how I want API calls to be structured."
-->

None

## 5. Documentation & References
<!-- 
  **Your Goal:** Provide links to official documentation for any libraries or APIs needed.
  This helps ensure current and correct implementation methods.
  **Example:** 
  - [React Docs](https://react.dev/)
  - [Currency API Docs](https://exchangerate-api.com/docs)
-->

- scikit-learn: Synthetic data generation (make_classification)
  https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_classification.html
- scikit-learn: StratifiedKFold CV
  https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html
- scikit-learn: Model evaluation metrics (ROC AUC, PR AUC, F1, etc.)
  https://scikit-learn.org/stable/modules/model_evaluation.html
- imbalanced-learn (SMOTE and pipelines)
  https://imbalanced-learn.org/stable/
- pandas documentation
  https://pandas.pydata.org/docs/
- NumPy documentation
  https://numpy.org/doc/
- Matplotlib documentation
  https://matplotlib.org/stable/
- Seaborn documentation
  https://seaborn.pydata.org/

## 6. Other Considerations & Gotchas
<!-- 
  **Your Goal:** List anything else important. Tricky parts? Specific constraints? Performance requirements?
  **Example:** "The API has a rate limit of 10 requests per minute, so add error handling for that."
-->

- Prevent data leakage: all preprocessing (scaling, SMOTE) must be inside a single `Pipeline` fitted only on training folds.
- Class imbalance: report both ROC AUC and PR AUC; tune decision threshold to hit target recall while keeping precision reasonable.
- Reproducibility: fix `random_state` across dataset generation, CV, and models; document seeds used.
- Runtime: aim for <60 seconds on a typical laptop; prefer small, interpretable models unless accuracy demands otherwise.
- Ethics & privacy: use synthetic data only; no PHI.

## 7. Success Criteria
<!-- 
  **Your Goal:** Define what "done" looks like. How will you know the project is successful?
  **Example:** 
  - User can convert between any two supported currencies
  - Conversion happens in under 2 seconds
  - Error messages are clear and helpful
-->

- ROC AUC ≥ 0.80 and PR AUC ≥ 0.35 on the held-out test set (with ~15% positives).
- Achieve recall ≥ 0.70 at precision ≥ 0.60 after threshold tuning on validation, then confirm on test.
- End-to-end pipeline (data synth → training → evaluation → artifact export) runs reproducibly with fixed seeds and saves outputs to `output/`.

## 8. ML Project Flag (manual)
<!-- 
  Set this flag explicitly to control ML workflow routing. 
  true  -> ML workflows (e.g., TRIPOD+AI pipeline)
  false -> Standard software workflows
  Example values: true | false
-->

is_ml_project: true
