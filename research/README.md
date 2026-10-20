# Lung-REA research code and data provenance

This directory provides analysis source code and documents the public data used in the study. The browser calculator remains at the repository root. Updating this documentation does not refit or recalibrate the model.

## Study populations and outcome

| Role | Population | Participants | Deaths within five years |
|---|---|---:|---:|
| Development and repeated nested internal validation | NHANES 2007-2012, ages 50-79 | See manuscript | See manuscript |
| Historical evaluation of the frozen full-development fit | NHANES III (1988-1994), ages 50-79 | See manuscript | See manuscript |

The outcome is **all-cause death within 60 months**. The final model is additive constrained ridge/spline logistic regression with 29 predictors and C=0.003. The risk-equivalent age is obtained by inverting the sex-specific reference risk curve over ages 50-79. Risks outside reference support receive a range flag without a numerical age.

The three modern survey cycles form one development population. Repeated nested cross-validation evaluates the modeling procedure, not the final coefficients in an independent sample. The final coefficients were fitted on all development participants. Historical outcomes did not update them, but both populations had been inspected previously; historical evaluation is exploratory. The model underestimated historical mortality; see the manuscript for results. No untouched contemporary or international validation is claimed.

## Start here

- [Public data sources and exact files](DATA_SOURCES.md)
- [Reproduction instructions and current limits](REPRODUCING.md)
- [Code inventory](CODE_MAP.md)
- [Predictor definitions and source variables](scoring/predictor_dictionary.csv)
- [External validation protocol](docs/EXTERNAL_VALIDATION_GUIDE_EN.md)
- [Recorded analysis environment](docs/environment.json)

No participant-level files, mortality rows, fitted pickle objects, credentials or raw downloads are distributed. Obtain survey files from NCHS and keep analytical records locally. The synthetic scoring fixtures are artificial cases, not sampled study participants.

## Existing public model

- Model SHA-256: `964e27d44b28f5b54b4ecb7c3a72da0c8639c61c7ac759bf28353979aeb3d5ad`
- Reference CSV SHA-256: `9e28a3809823d4316abaf9d1ca18a970d6ba7495abef846e87879bd07bbc07dd`

[Verify these files and synthetic scoring](REPRODUCING.md#1-verify-the-released-scorer) before applying them. A newly fitted model requires its own version and evaluation. The public model estimates mortality risk, not lung tissue age, life expectancy or treatment effects. Clinical benefit has not been tested.

## Later conditional transport analysis

The [GBCS analysis code and assumptions](GBCS_CONDITIONAL_ANALYSIS.md) are available separately. This update publishes code/documentation only, without GBCS data or results, and does not alter the final NHANES model.
