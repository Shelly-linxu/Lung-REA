# Conditional GBCS transport diagnostic

This optional script documents the exploratory analysis added after the NHANES model was finalized. It does not change model parameters or the browser calculator. No GBCS records or derived study results are included in this GitHub update.

The script reads locally authorized `gbcs_main.dta` and `newvital_2026.dta`, restricts to phase 1, checks eligibility and baseline measurements, uses calendar five-year outcome dates, calculates GLI Global z scores using the existing browser implementation, and applies the final model without updating. It exports aggregate sample selection, scenario performance, calibration, subgroup estimates and conditional bootstrap intervals. It saves no participant predictions.

## Important interpretation

This is **not complete external validation**. The equivalent income-to-poverty ratio and heart-failure variables were not verified. Six predeclared scenarios fix income ratio to 1, 3 or 5 and heart failure to 0 or 1. The all-heart-failure scenario is a stress test. Phase-1 PEF is interpreted as L/s under an unverified assumption; the CLI requires that assumption to be acknowledged explicitly. COPD and other questionnaire mappings are proxies requiring source review. Plausibility checks do not establish spirometry maneuver quality.

All scenarios must be reported. Identical AUROC across uniform additive input changes follows from preserved ranking and does not prove robustness to the true individual values. Bootstrap intervals condition on the assumptions and saved predictions; they do not measure uncertainty in variable equivalence or PEF units. No model selection, recalibration or direct PARS comparison is performed.

## Run locally

Use the Python dependencies in `requirements.txt` and Node.js available on PATH. Keep output outside this public Git checkout.

```sh
python research/code/gbcs_conditional_transport.py \
  --data-dir /your/authorized/GBCS \
  --output-dir /your/local/conditional_results \
  --pef-unit-assumption L/s
```

Access to GBCS data must be obtained through the study's access arrangements. This repository grants no access or redistribution rights. The script is not a public-data download workflow. No research findings are uploaded by running it; execution performs no network requests.
