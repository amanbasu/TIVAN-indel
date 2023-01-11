###############################################################################################################################################
# This is a R stand-alone based R script for retrieving pre-computed functional scores for noncoding small indels across 44 tissues/cell types
# Usage: R --slave --args --no-save arg1 arg2 arg3 arg4 < TIVAN-indel.R 
# Example: R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda output.txt  < TIVAN-indel.R 
# Example: R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda output.txt  < TIVAN-indel.R 

# Args:
# arg1:  Input region: regionfile of small indels. The file has three columns "chr start end" with space/tab-delimited (chr1 10001 20000)
# arg2:  A file of all known 1000 Genome indels
# arg3:  A file/files of pre-computed score of 1000 Genome indels, multiple files are separated by comma
# arg4:  A output file contains retrieved scores for matched indels or indels in query region
# *** Note:  The R script and all files should be under the same directory


suppressMessages(library(GenomicRanges))
suppressMessages(library(data.table))


args=commandArgs()
narg=length(args)
if(narg!=8){
  stop("\n Wrong number of input parameters!",
       "\n arg1.Input region: regionfile of small indels. The file has three columns 'chr start end' with space/tab-delimited such as chr1 10001 20000)",
       "\n arg2.A file of all known1000 Genome indels",
       "\n arg3.A file/files of tissue-specific functional score of 1000 Genome indels, multiple files are separated by comma",
       "\n arg4.Output file",
       "\n Usage: R --slave --args --no-save arg1 arg2 arg3 arg4 < TIVAN-indel.R",
       "\n Example1: R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda output.txt  < TIVAN-indel.R",
       "\n Example2: R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda,Adipose_Visceral_Omentum.score.rda output.txt  < TIVAN-indel.R",
       
  )
}


regionfile=args[5]
indelfile=args[6]
scorefile=args[7]
outfile=args[8]




cat("************************************************\n")
cat(paste("There are total ",narg-4," parameters\n"))
cat(paste("		1.The Input indel region (two columns with chromosome and position (chr1 10000) or four columns including ref/alt alleles (chr1 10000 A AT): ",regionfile,"\n",sep=""))
cat(paste("	 	2.A file of all known1000 Genome indels: ",indelfile,"\n"))
cat(paste("		3.A file/files of pre-computed score of 1000 Genome indels, multiple files are separated by comma: ",scorefile,"\n",sep=""))
cat(paste("		4.The output file is: ",outfile,"\n"))
cat("************************************************\n")



print('Load query indels/regions!')
region=fread(regionfile)
region=as.data.frame(region)
colnames(region)=c('chr','start','end')
region.gr=GRanges(seqnames=Rle(region$chr),ranges=IRanges(region$start,region$end))




print('Load noncoding small indels in 1000 Genomes!')
load(indelfile)


print('Load pre-computed score for noncoding small indels in 1000 Genomes')
scores=NULL
scorelist=strsplit(scorefile,split='\\,')
scorelist=unlist(scorelist)
for(i in 1:length(scorelist)){
  load(scorelist[i])
  scores=cbind(scores,score)
}

tissuenames=gsub('.score.rda','',scorelist)
colnames(scores)=tissuenames
score=scores
rm(scores)


print('Output the scores!')
o=findOverlaps(region.gr,sindel.noncoding.1kg)
a=region.gr[queryHits(o)]
b=sindel.noncoding.1kg[subjectHits(o)]

if(length(scorelist)>1){
  score.out=score[subjectHits(o),]
  out.df=cbind(as.data.frame(a)[,1:3],as.data.frame(b)[,c(1:3,6,7)],score.out)
  colnames(out.df)=c('query.chr','query.start','query.end','1kg.chr','1kg.start','1kg.end','ref','alt',tissuenames)
}else{
  score.out=score[subjectHits(o)]
  out.df=cbind(as.data.frame(a)[,1:3],as.data.frame(b)[,c(1:3,6,7)],score.out)
  colnames(out.df)=c('query.chr','query.start','query.end','1kg.chr','1kg.start','1kg.end','ref','alt',tissuenames)
}


write.table(out.df,file=outfile,row.names = F,col.names=T,sep='\t',quote=F)


