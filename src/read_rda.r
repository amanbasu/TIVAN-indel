library(stringr)

base_path = '../data/'
tissue = 'CD4_NAIVE'

load(paste0(base_path, tissue, '.trainingset.rda'))

df_pos <- data.frame(annot.pos)
df_neg <- data.frame(annot.neg)
df <- rbind(df_pos, df_neg)
write.table(df, file=paste0(base_path, tissue, '.annot.csv'), quote=F, sep=",", row.names=F)