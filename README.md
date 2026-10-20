# Lung-REA calculator

A bilingual English/Chinese browser calculator for **Lung Risk–Equivalent Age** and five-year **all-cause** mortality risk. The tool uses the single frozen 29-predictor additive constrained ridge/spline model (C=0.003). No model fitting, recalibration or parameter updating occurs in the browser.

## Use

**[Open the online calculator](https://shelly-linxu.github.io/Lung-REA/)** — English / 中文.

Open `index.html` in a browser; no build, server or internet connection is required after downloading the repository. On GitHub use **Code → Download ZIP**, extract all files, and open `index.html`. If GitHub Pages is enabled, the same files work as a hosted static website.

1. Enter the required age, sex, height, peak expiratory flow, smoking status, and FEV₁/FVC **GLI Global z scores**.
2. Add known baseline smoking, clinical, socioeconomic and blood measurements. Unknown optional values use frozen development imputation constants and are listed in the result. Unknown diagnoses are not silently treated as “No”.
3. Calculate. Toggle **English / 中文** without losing entered values or the result.
4. Download CSV or JSON. Exports include entered values, scored values, imputed fields, full-precision results, model/reference hashes, version and time. Input edits invalidate prior results.

The example is fictional, not a patient record. There is no bulk upload in this first release.

## Inputs and units

- Baseline age: 50–79 years; height: **cm**, 120–210; peak expiratory flow: **L/min**, 60–1,000. The UI converts height to meters and peak flow to PEF/100 L/min for scoring.
- FEV₁ and FVC: dimensionless **GLI Global z scores**, not raw volumes, FEV₁/FVC ratio, or percent predicted. This release does not compute z scores from raw spirometry. Obtain them using an independently validated GLI Global implementation; the study's R helper `compute_gli_zscores.R` is provided.
- Smoking duration is an elapsed-years proxy, not pack-years. Current smoking intensity is harmonized to 0–95 cigarettes/day. Years since quitting is relevant to former smokers.
- WBC: ×10⁹/L; hemoglobin and albumin: **g/dL**; RDW and lymphocytes: **%**. Albumin g/L must be divided by 10 before entering it.
- Optional disease history and symptoms use Yes/No/Unknown. Lower education approximates less than high school. Income-to-poverty ratio is capped at 5 in the study.

See `predictor_dictionary.csv` for source definitions. The UI adds plausibility checks to guard against unit errors; it cannot adjudicate spirometry quality, diagnosis or data provenance. Measurements should follow the study eligibility/quality criteria.

## Interpretation and limits

Lung-REA is the age of a same-sex reference individual with the same predicted five-year all-cause mortality risk. It is **not** life expectancy, a diagnosis, or a direct measurement of biological pulmonary aging. The model was developed in eligible NHANES 2007–2012 participants aged 50–79 (n=4,915; 243 five-year deaths). NHANES III evaluation (n=4,633; 434 deaths) was historical and previously inspected; risk was underestimated (6.28% predicted versus 9.37% observed). This is a research tool, not an established basis for clinical decisions.

The sex-specific reference covers ages 50–79. Out-of-reference risk returns a direction flag (`below_reference_age_50` or `above_reference_age_79`) and no numerical age or age gap. The UI shows <50 or >79 explicitly as a flag; it does not clip or extrapolate. Only 47.6% of historical records had supported numerical ages; risk estimates remain available for all eligible inputs.

## Privacy

Calculations run entirely on the user's device. No input submission, analytics, cookies, persistent local storage, external fonts or remote scoring services are used. The page's content security policy prohibits network connections from scripts and form submissions. A hosted page still involves ordinary requests to its hosting provider for the site files; entered measurements are not included in these requests. Downloaded result files contain health measurements and should be stored appropriately. Reset clears the form in memory.

## Frozen model identity

- Model SHA-256: `964e27d44b28f5b54b4ecb7c3a72da0c8639c61c7ac759bf28353979aeb3d5ad`
- Reference SHA-256: `9e28a3809823d4316abaf9d1ca18a970d6ba7495abef846e87879bd07bbc07dd`
- App version: `Lung-REA-web-1.0.0`

`frozen_model.json` is byte-identical to the final research model. `model-data.js` embeds that specification and the age/risk columns from the original reference CSV at full precision. `MODEL_IDENTITY.json` is the original research-release identity file; its Python scorer hashes document provenance and do not identify JavaScript files. No participant-level study data are included in this repository.

## Verification

The JavaScript engine was compared locally against the frozen Python scorer on all 9,548 retained study records: maximum risk absolute difference <5×10⁻¹⁶; maximum supported-age difference <2×10⁻¹³ years; all range flags agree. Only aggregate audit values are distributed (`tests/numerical-verification.json`). `tests/synthetic-fixtures.json` contains 80 randomly generated artificial cases with Python reference results, not sampled cohort rows.

Run the portable numerical checks with Node:

```sh
node tests/core.test.cjs
```

The separate browser test covers language switching, unit conversion, missing-data disclosure, downloads, invalid-input rejection, unsupported-age flags, stale results, smoking-state controls and a 390px responsive layout. Its local Playwright/Chrome paths must be adjusted for another machine. Browser-test output contains fictional data only.

## Implementation

- `core.js`: frozen scoring, cubic B-spline bases with linear tails, monotone interval bases, and reference inversion.
- `app.js`, `index.html`, `style.css`: bilingual interface and local downloads.
- `model-data.js`: aggregate parameters and reference curves.
- `MODEL_CARD_EN.md`, `predictor_dictionary.csv`: research context and predictor provenance.

Implementation agreement does not establish clinical validity or a benefit of communicating risk as an age. Changes to the frozen model require a new model version and separate evaluation.
