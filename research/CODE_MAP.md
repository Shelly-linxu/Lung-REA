# Code inventory

| File or directory | Purpose | Execution status |
|---|---|---|
| `scoring/predict_lung_rea.py` | Validate engineered inputs, calculate five-year risk and invert the reference curve | Portable; uses adjacent public JSON and embedded reference curves at the repository root |
| `scoring/score_frozen.py` | Reconstruct standardized bases and frozen logistic prediction | Portable; no fitting |
| `scoring/compute_gli_zscores.R` | Convert measured FEV1/FVC to GLI Global z scores with rspiro | Function; requires R and the recorded package version |
| `scoring/verify_release.py` | Verify hashes and score 80 artificial test cases | Portable; no cohort data |
| `code/development/core.py` | Predictor panels, sign constraints, splines, optimization, boosting and reference construction | Original final-development implementation |
| `code/development/run.py` | Three repetitions of nested five-outer/three-inner-fold validation, final selection and refit | Requires locally prepared candidate table; computationally intensive |
| `code/NHANES_stability_v20/direct_core.py` | AUROC, Brier, log loss and diagnostic calibration calculations | Metrics dependency only; contains no previous model |
| `code/development/prepare.py` | Original laboratory expansion and merge | Provenance; depends on original workspace paths and prior candidate preparation |
| `code/comparators/published_equations.py` | Six published age equations with their units | Reusable equation functions |
| `code/comparators/score_mappings.py` | Frozen study-fitted age/sex mortality mappings | Reusable scoring functions |
| `code/evaluate_frozen.py` | Direct historical scoring without fitting or recalibration | Portable with local engineered inputs and outcomes |
| `code/preparation_provenance/` | Original historical parsing, phenotype coding, laboratory preparation and subgroup/flow reporting | Audit scripts with original relative paths; not a standalone raw-data pipeline |

The historical folder name `NHANES_stability_v20` is retained solely to satisfy the original core import. The development class name `Expanded` is also retained for provenance. Neither identifies an alternative model for deployment. The saved amendment mentions earlier temporal diagnostics; no separately fitted temporal model is part of this final release.

Preparation scripts retain original project-relative paths so the provenance is visible. They must not be presented as a one-command workflow from raw data. Follow `REPRODUCING.md` for what can be run directly and which prerequisites remain local.
