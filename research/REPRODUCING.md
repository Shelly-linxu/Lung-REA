# Reproducing scoring and analysis

## 1. Verify the released scorer

From the repository root, use Python with the versions recorded in `research/docs/environment.json`. Install `research/requirements.txt` in your own analysis environment if needed. R GLI preprocessing additionally used `rspiro` 0.5.

```sh
python research/scoring/verify_release.py
```

This checks the existing public model hash, then compares Python results with 80 already-public artificial scoring fixtures. Reference risks are read from the existing public model-data.js file; no model artifacts are added in this documentation update. It reads no cohort data and performs no fitting. The browser tests remain available as `node tests/core.test.cjs` and `node tests/gli.test.cjs`.

## 2. Score an independent population

Prepare one row per participant, with all columns in `research/scoring/input_template.csv` and the definitions in `predictor_dictionary.csv`. The template is a header, not a study record. The Python scorer accepts engineered GLI Global z scores; the browser additionally converts raw FEV1/FVC locally. `compute_gli_zscores.R` provides the research conversion function.

```sh
python research/scoring/predict_lung_rea.py /your/local/inputs.csv /your/local/results.csv
```

Keep inputs and outputs outside the repository or in ignored `research/private/`. Mandatory physiology and smoking states must be observed; optional sporadic missingness uses frozen development constants. A population lacking an entire required panel is not suitable for faithful application.

For a local table that also contains `e5` (binary five-year all-cause outcome), evaluate the frozen model without updating:

```sh
python research/code/evaluate_frozen.py /your/local/inputs_with_e5.csv /your/local/evaluation
```

This writes participant predictions locally and aggregate performance/calibration. It does not fit a model or recalibrate. A short follow-up record cannot simply be labeled a five-year survivor. Follow the [external validation protocol](docs/EXTERNAL_VALIDATION_GUIDE_EN.md) for endpoint and censoring decisions in another population.

## 3. Re-run development

The original training implementation is in `research/code/development/`. It expects a locally prepared `candidate_data_LOCAL_ONLY.csv` in that directory, with all 29 engineered predictors plus:

- `cohort`: `NHANES_2007_2012` or `NHANES_III`.
- `uid`: unique participant key; `cycle`, `stratum`, `psu`, `weight`.
- `e5`: verified five-year all-cause event indicator.

The code filters development rows and asserts 4,915 participants and 243 deaths. It does not use historical rows to select parameters. All preprocessing is estimated within each training fold.

```sh
python research/code/development/run.py
```

The run uses three repetitions, five outer folds, three inner folds, 50 regression candidates and eight boosting candidates. It saves OOF predictions, selected candidates and a separate final full-development fit. It can be computationally expensive. Generated participant outputs and pickle objects are ignored by Git. Do not copy newly fitted parameters over `research/scoring/` or the browser model; a new fit is a different model version.

## 4. What is and is not reproduced automatically

Frozen risk/age scoring and its synthetic checks are portable. Development fitting is runnable once the harmonized input table is prepared. Exact source-to-table preparation currently requires reconstructing the documented upstream joins and quality filters; the repository does **not** yet offer a tested one-command pipeline from raw CDC downloads to all manuscript results. Original preparation/reporting scripts retain project-relative dependencies and are provided for audit.

Results depend on the exact 2019 mortality linkage, source versions, eligibility, variable coding and numerical environment. Re-running on a later mortality release would be a new analysis. We have not rerun full model selection as part of this documentation release. The existing public model and embedded reference values are unchanged.

Six classic lung-age equations and source code for scoring study-fitted mortality mappings are included under `code/comparators/`. Mapping parameters remain in the local analysis package. These mappings were trained for this study, not published as part of the original age equations. Comparisons used identical participants aged 50-70, with finite outputs from all equations. Lung-REA has a broader predictor set; better performance does not isolate an algorithmic advantage.

## 5. Interpretation of the evidence

Development and historical populations had both been inspected earlier. Nested internal validation cannot erase the wider model search. Report historical underprediction without changing probabilities from validation outcomes. Bootstrap confidence intervals condition on saved predictions and omit full model-selection uncertainty, survey clustering and multiplicity. The research calculator has not demonstrated clinical benefit.
