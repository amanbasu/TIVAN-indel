library(stringr)

tissue = 'CD4_NAIVE'
base_path = '../res/'
rda_file = paste0(base_path, tissue, '.trainingset.rda')

load(rda_file)

df <- data.frame(annot.pos)
write.table(df, file=paste0(base_path, tissue_name, '.annot_pos.csv'), quote=F, sep=",", row.names=F)
rm(df)

df <- data.frame(annot.neg)
write.table(df, file=paste0(base_path, tissue_name, '.annot_neg.csv'), quote=F, sep=",", row.names=F)
rm(df)