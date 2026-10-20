# Final Lung-REA model

Lung-REA means Lung Risk–Equivalent Age. One final constrained ridge/spline logistic model predicts five-year all-cause death; a sex-specific development-derived reference converts supported probabilities to a risk-equivalent age. It is a research model, not a validated tissue-age or life-expectancy measure.

## Development and final parameters
Development data are NHANES 2007–2012, ages 50–79, n 4,915 with 243 deaths by 60 months. Final raw input count 29. Final penalty C=0.003. The final full-development specification is additive, without interaction terms. Imputation, knots, scaling, coefficients and healthy reference values are fixed from development. Full precision is in frozen_model.json; MODEL_IDENTITY.json stores release hashes. The original parameter and reference files are byte-identical to the original frozen artifacts.

## Evaluation roles
Repeated nested internal OOF probabilities assess a development procedure; they do not come from the single final full-development coefficient vector. NHANES III (n 4,633;434 deaths) is separately scored using that final fixed model. No coefficient, imputation constant, reference value or baseline-risk level was updated using historical outcomes. Previous data inspection prevents a claim of untouched confirmation. The separately trained forward temporal model is excluded from the final release.

## Executable use
predict_lung_rea.py reads all 29 engineered predictor columns and returns risk_5y, lung_rea_years and age_status. Use predictor_dictionary.csv for names and units. GLI z-score calculation and spirometry-quality adjudication must precede scoring. All column names are required; optional sporadic missing values use frozen constants. Mandatory core measurements must be available. Unsupported baseline ages, invalid binary coding, overlapping smoking states, missing core fields and absent predictor columns are rejected.

Command from this directory: python predict_lung_rea.py input.csv output.csv

The utility was verified against all 9,548 retained records without model fitting. It reproduced final-fit probabilities exactly relative to the frozen standalone scorer and reproduced saved historical probabilities to numerical precision. Individual outputs are not distributed. Only aggregate verification is provided.

## Interpretation limits
The unweighted model targets the eligible analytical sample. Historical all-cause risk is underestimated. Only 55.7% of development training records and 47.6% of historical records have in-range numerical age from the final model; strict repeated-validation support is 46.6%. These are different evaluation roles and are not interchangeable. All participants retain risk estimates. The age conversion is bounded at 50–79 with no clipping or extrapolation. Full mortality-risk AUROC must not be described as direct numerical-age AUROC.

## Finalization scope
This release finalizes the specification and reproducible implementation. It does not establish clinical readiness or eliminate the need for independent contemporary calibration, pulmonary-specific validity, subgroup assessment and clinical-utility evaluation. Original development plans, freeze hashes and source code are retained. Future revisions require a separately identified model version, not silent changes to these parameters.
