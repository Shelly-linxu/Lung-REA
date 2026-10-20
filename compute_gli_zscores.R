# GLI Global engineering used in Lung-REA; developed with rspiro 0.5.
# Inputs: age years, height meters, male 0/1, FEV1/FVC liters.
compute_gli_zscores <- function(age, height, male, fev1_liters, fvc_liters) {
  stopifnot(length(age)==length(height), all(male %in% c(0,1)))
  sex <- ifelse(male==1, 1, 2)
  z <- rspiro::zscore_GLIgl(age, height, sex, FEV1=fev1_liters, FVC=fvc_liters)
  data.frame(zFEV=z$z.score.FEV1, zFVC=z$z.score.FVC)
}
