# Third-party attribution

The GLI Global conversion in `gli-global.js` and lookup data in `gli-data.js` derive from **rspiro 0.5**, copyright Theodore Lytras, licensed under **GPL-2.0-or-later**. Source: https://github.com/thlytras/rspiro . Scientific reference: Bowerman et al., *A Race-neutral Approach to the Interpretation of Lung Function Measurements*, DOI https://doi.org/10.1164/rccm.202205-0963OC .

The JavaScript port preserves the study implementation, including quarter-year spline lookup. Corresponding R function sources are supplied in `tests/rspiro-0.5-source.txt`; `tests/export-gli-reference.R` documents export from the installed package. These tables are published reference coefficients, not participant records. `COPYING` contains GPL version 2.

This application is distributed under GPL-2.0-or-later, without warranty. Licensing does not establish clinical validity. The GLI conversion does not refit or alter the frozen Lung-REA prediction model.
