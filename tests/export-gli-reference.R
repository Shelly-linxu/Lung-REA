# Export the exact rspiro 0.5 GLI Global implementation used in model development.
# Set RSPIRO_LIB to a nonstandard library if needed. No participant data are used.
lib <- Sys.getenv('RSPIRO_LIB'); if (nzchar(lib)) .libPaths(c(lib,.libPaths()))
stopifnot(requireNamespace('rspiro',quietly=TRUE), as.character(packageVersion('rspiro'))=='0.5')
stopifnot(requireNamespace('jsonlite',quietly=TRUE))
args <- commandArgs(trailingOnly=TRUE); dest <- if(length(args))args[1] else '.'
q <- getFromNamespace('GLIgl_lookup','rspiro'); q <- q[q$f %in% c('FEV1','FVC') & q$agebound>=50 & q$agebound<=79,]
writeLines(jsonlite::toJSON(q, dataframe='rows',digits=NA),file.path(dest,'gli-lookup.json'))
# Full source counterpart for attribution/audit.
writeLines(c('# rspiro 0.5, Theodore Lytras; GPL >=2',capture.output(getFromNamespace('getLMS_GLIgl','rspiro')),capture.output(rspiro::zscore_GLIgl),capture.output(getFromNamespace('rspiro_check_somat','rspiro'))),file.path(dest,'rspiro-0.5-source.txt'))
# Artificial vectors include quarter-year boundaries and decimal ages.
set.seed(20261020);n<-500
age<-c(50,79,60.249999,60.25,60.250001,runif(n-5,50,79));height<-runif(n,1.2,2.1);male<-rep(0:1,length.out=n);fev<-runif(n,.5,7);fvc<-pmax(fev,runif(n,.5,10))
z<-rspiro::zscore_GLIgl(age,height,ifelse(male==1,1,2),FEV1=fev,FVC=fvc)
x<-data.frame(age,height,male,fev1_l=fev,fvc_l=fvc,zFEV=z$z.score.FEV1,zFVC=z$z.score.FVC)
writeLines(jsonlite::toJSON(x,dataframe='rows',digits=NA),file.path(dest,'gli-reference-fixtures.json'))
