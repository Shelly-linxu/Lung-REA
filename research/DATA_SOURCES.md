# Public data sources

The study used public CDC/NCHS NHANES examination, questionnaire, laboratory and linked mortality files. This repository provides source links and coding information, not copies of individual records. Official documentation links were checked on 20 October 2026.

## NHANES 2007-2012: development

Official cycle pages: [2007-2008](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2007), [2009-2010](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2009), [2011-2012](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2011).

Download the following XPT modules for each cycle. Suffixes are E (2007-2008), F (2009-2010) and G (2011-2012). For example, `SPX_E.xpt` and `CBC_G.xpt`.

| Module | Measures used | Documentation example |
|---|---|---|
| DEMO | Age, sex, education, income-to-poverty ratio, examination weights, strata and PSU | [DEMO_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DEMO_E.htm) |
| SPX | Baseline pre-bronchodilator FEV1, FVC, peak flow, status and quality grades | [SPX_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/SPX_E.htm) |
| BMX | Measured height and BMI | [BMX_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BMX_E.htm) |
| SMQ | Smoking status, current cigarettes/day, initiation and cessation ages | [SMQ_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/SMQ_E.htm) |
| MCQ | Asthma, emphysema, chronic bronchitis and cardiovascular history | [MCQ_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/MCQ_E.htm) |
| RDQ | Cough, phlegm and wheeze | [RDQ_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/RDQ_E.htm) |
| BPQ | Hypertension history | [BPQ_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/BPQ_E.htm) |
| DIQ | Diabetes history | [DIQ_E](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2007/DataFiles/DIQ_E.htm) |
| CBC | WBC, hemoglobin, RDW and lymphocyte percentage | [CBC_G](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/CBC_G.htm) |
| BIOPRO | Serum albumin | [BIOPRO_G](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BIOPRO_G.htm) |

Within each cycle, join by `SEQN` and verify unique keys. Preserve cycle labels and survey design fields. `SPXNFEV1` and `SPXNFVC` are in mL: divide by 1,000 for liters. `SPXNPEF` is mL/s: multiply by 0.06 for L/min, then divide by 100 for model input `pef100`. Height is cm: divide by 100 for meters. Derive GLI Global z scores using age, height, sex and measured lung volumes; do not substitute percent predicted.

## NHANES III: historical evaluation

Use the official [NHANES III data files page](https://wwwn.cdc.gov/nchs/nhanes/nhanes3/datafiles.aspx), core Release 1A:

- Household adult: `adult.dat`, layout `adult.sas`, adult codebook.
- Examination: `exam.dat`, layout `exam.sas`, examination codebook.
- Laboratory: `lab.dat`, layout `lab.sas`, laboratory codebook.

These are fixed-width files. Parse positions from the corresponding SAS INPUT layouts; do not read them as delimited CSVs. Join by `SEQN` after checking uniqueness. The source laboratory layout is [lab.sas](https://wwwn.cdc.gov/nchs/data/nhanes3/1a/lab.sas); [laboratory codebook](https://wwwn.cdc.gov/nchs/data/nhanes3/1a/lab-acc.pdf).

Historical FEV1 and FVC are `SPPFEV1` and `SPPFVC`; peak flow is `SPPPEAK`. Core eligibility uses MEC spirometry, reliability and reproducibility flags, at least two maneuvers and directly measured height. The exact raw variables and coding for all 29 predictors are in [predictor_dictionary.csv](scoring/predictor_dictionary.csv). Historical laboratory fields are `WCPSI`, `HGP`, `RWP`, `LMPPCNT` and `AMP`. Units were aligned with modern measurements; this does not establish assay equivalence.

## Linked mortality: 2019 public-use release

Use the NCHS [public-use linked mortality files](https://www.cdc.gov/nchs/linked-data/mortality-files/) and the accompanying read-in programs and file description. The analysis used the **2019 linkage**, not a later release. A documented source archive is the [CDC Stacks 2019 public-use package](https://stacks.cdc.gov/view/cdc/117141).

Required files are `NHANES_III_MORT_2019_PUBLIC.dat`, `NHANES_2007_2008_MORT_2019_PUBLIC.dat`, `NHANES_2009_2010_MORT_2019_PUBLIC.dat`, and `NHANES_2011_2012_MORT_2019_PUBLIC.dat`.

The analysis reads `SEQN`, eligibility, vital status, leading-cause group and examination-based follow-up months. The inherited official NHANES layout uses Python half-open column ranges `(0,6)`, `(14,15)`, `(15,16)`, `(16,19)` and `(45,48)`, respectively; check these against the release-specific official read-in program before parsing. Join within survey by `SEQN`, then verify unique cohort/SEQN keys.

The event is death with recorded examination follow-up <=60 months. Retained non-events must have sufficient follow-up to establish five-year survival. Public-use follow-up perturbation and grouped causes limit interpretation. The final model predicts all-cause mortality. The small respiratory-death counts do not support a respiratory-specific validation claim.

## Selection, missingness and provenance

See the manuscript selection diagram for retained/excluded counts and [predictor_dictionary.csv](scoring/predictor_dictionary.csv) for source coding. The development input table was assembled locally through earlier preprocessing stages. Archived scripts show the historical parser, phenotype additions and laboratory merge; they do not constitute a complete automatic raw-data reconstruction pipeline.

Optional sporadic missing values use training-only constants. Entire missing predictor panels must not be replaced by those constants. Neither ELSA, GBCS, UK Biobank nor another country's records contribute to this final fit or its historical evaluation.

Researchers should obtain public files directly from NCHS, retain local source checksums, and follow the NCHS analytic guidance and release-specific conditions. No CDC/NCHS endorsement of Lung-REA is implied.
