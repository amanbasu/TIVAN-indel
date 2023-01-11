
##################
# This function prepares CADD annotation, reference and alternative sequence for query small indels
# The output reference and alternative sequence will be used for deep learning model to predict multi-omics features 
# Usage: R --slave --args --no-save CADD.indel.rda snp.pos.txt snp.neg.txt test  <  prepare.R 



##################
#  load librarys


suppressMessages(library(BSgenome.Hsapiens.UCSC.hg19))
suppressMessages(library(data.table))


##################
#  load functions


imputeNA<-function(annot){
  mean.na=apply(is.na(annot),2,mean)
  id.no=which(mean.na>0)
  if(length(id.no)>0){
    for(i in 1:length(id.no)){
      annot[,id.no[i]][is.na(annot[,id.no[i]])]=median(annot[,id.no[i]][!is.na(annot[,id.no[i]])])
    }
  }
  annot
}



batchReplaceIndel<-function(gr,ext=500){
  
  nseq=length(gr)
  gr.ext=gr
  start(gr.ext)=start(gr.ext)-ext
  end(gr.ext)=end(gr.ext)+ext
  len=end(gr.ext)[1]-start(gr.ext)[1]+1
  seqs.ref=getSeq(BSgenome.Hsapiens.UCSC.hg19,gr.ext)
  seqs.alt=NULL
  
  
  for(i in 1:nseq){
    
    pos1=GRanges(seqnames(gr.ext)[i],ranges=IRanges(start(gr.ext)[i],start(gr)[i]-1))
    
    seq1=getSeq(BSgenome.Hsapiens.UCSC.hg19,pos1)
    
    len1=nchar(seq1)
    
    nref=nchar(gr.ext$ref[i])
    
    seq2=DNAStringSet(gr.ext$alt[i])
    
    len2=nchar(seq2)
    
    len3=len-len1-len2
    
    pos3=GRanges(seqnames(gr.ext)[i],ranges=IRanges(start(gr)[i]+nref,start(gr)[i]+nref+len3-1))
    
    seq3=getSeq(BSgenome.Hsapiens.UCSC.hg19,pos3)
    
    len3=nchar(seq3)
    
    len1+len2+len3
    
    seq.alt=xscat(seq1,seq2,seq3)
    
    seqs.alt=c(seqs.alt,seq.alt)
    
  }
  
  seqs.alt=DNAStringSet(do.call(c,unlist(seqs.alt)))
  
  
  list(seqs.ref=seqs.ref,seqs.alt=seqs.alt,gr=gr)
  
}



###############################
#  arguments for main function


args=commandArgs()
CADDfile=args[5]
posfile=args[6]
negfile=args[7]
outpath=args[8]


narg=length(args)
if(narg!=8){
  stop("\n Wrong number of input parameters!",
       "\n arg1. CADD.indel.rda",
       "\n arg2. The file has five columns 'chr start end ref alt' with space/tab-delimited such as chr1 10001 20000 A AT)",
       "\n arg3. The file has five columns 'chr start end ref alt' with space/tab-delimited such as chr1 10001 20000 A AT)",
       "\n arg4. Output path for CADD annotation and indel sequences",
       "\n Usage: R --slave --args --no-save arg1 arg2 arg3 arg4 < prepare.R",
  )
}




print('Load CADD annotations...')

load(CADDfile)


print('Obtain CADD annotations...')

maxlen=100

m=fread(posfile)
snp.pos=GRanges(seqnames = Rle(m$chr), ranges = IRanges(m$start,m$end))
snp.pos$ref=m$ref
snp.pos$alt=m$alt
snp.pos=snp.pos[nchar(snp.pos$ref)<maxlen & nchar(snp.pos$alt)<maxlen]


m=fread(negfile)
snp.neg=GRanges(seqnames = Rle(m$chr), ranges = IRanges(m$start,m$end))
snp.neg$ref=m$ref
snp.neg$alt=m$alt
snp.neg=snp.neg[nchar(snp.neg$ref)<maxlen & nchar(snp.neg$alt)<maxlen]


m.pos=match(snp.pos,chrmat.gr.all)
annot.pos=chrmat.all[m.pos[!is.na(m.pos)],]
snp.pos=snp.pos[!is.na(m.pos)]

m.neg=match(snp.neg,chrmat.gr.all)
annot.neg=chrmat.all[m.neg[!is.na(m.neg)],]
snp.neg=snp.neg[!is.na(m.neg)]

message('The sample size for positive set is: ',length(snp.pos),'; The sample size for negative set is: ',length(snp.neg))

annot.pos=imputeNA(annot.pos)

annot.neg=imputeNA(annot.neg)

annot=rbind(annot.pos,annot.neg)

annot=annot[,-c(46,47)]

write.table(annot,file=file.path(outpath,'annot.csv'),row.names=F,col.names=T,sep = ',',quote=F)


print('Obtain fasta sequences.....')

snp.pos.res=batchReplaceIndel(snp.pos,ext=500)
writeXStringSet(snp.pos.res$seqs.ref,file=file.path(outpath,'snp.pos.ref.fasta'))
writeXStringSet(snp.pos.res$seqs.alt,file=file.path(outpath,'snp.pos.alt.fasta'))
              
snp.neg.res=batchReplaceIndel(snp.neg,ext=500)
writeXStringSet(snp.neg.res$seqs.ref,file=file.path(outpath,'snp.neg.ref.fasta'))
writeXStringSet(snp.neg.res$seqs.alt,file=file.path(outpath,'snp.neg.alt.fasta'))


