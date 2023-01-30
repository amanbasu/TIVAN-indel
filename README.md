# TIVAN-indel: A computational framework for annotating and predicting noncoding regulatory small insertions and deletions

Paper link: https://doi.org/10.1093/bioinformatics/btad060

By leveraging labelled noncoding sindels identified by cis-expression quantitative trait loci (cis- eQTLs) analyses across 44 tissues in GTEx, and a compilation of both generic functional annotations and tissue-specific multi-omics features, we developed TIVAN-indel, which is a supervised computational framework for predicting noncoding sindels that potentially regulate the nearby gene expression. 

<p align="center"><img src="res/overview.png" alt="Overview"></p>
<p align="center">Figure 1. Overview of the TIVAN-Indel.</p>

## Requirements

TIVAN-Indel is implemented by both R and Python and the requirements are

### Python (3.9.6) packages

```
xgboost==1.5.1
h5py==3.1.0
matplotlib==3.4.3
numpy==1.19.3
numpy-utils==0.1.6
pandas==1.4.0
scikit-learn==0.24.2
tensorflow==2.6.0
```

### R (4.1.1) packages
```
BSgenome.Hsapiens.UCSC.hg19
data.table
```

## Usage

Download TIVAN-Indel

```bash
git clone https://github.com/amanbasu/TIVAN-indel.git
```

Install requirements for Python

```bash
pip install -r requirements.txt
```

Install requirements for R

```r
install.packages('data.table')
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install("BSgenome.Hsapiens.UCSC.hg19")

```



### Prepare training data

We use a compilation of both generic functional annotations and tissue-specific functional annotations to train the TIVAN-indel model. Given query sindels (example: [train/snp.pos.txt](train/snp.pos.txt)), R script `prepare.R` will generated (1) CADD annotations for query sindels and (2) reference genomic sequence and alterntive genomic sequence with sindels. The rda file `CADD.indel.rda` contains the CADD annotations for all indels in 1000 Genome Project can be downloaded [here](https://drive.google.com/file/d/1Eio1YYZNmrVIoqFg6r-GUTGuwjudi30P/view?usp=share_link).


Running the R command line with four arguments

```bash
R --slave --args --no-save CADD.indel.rda train/snp.pos.txt train/snp.neg.txt train  <  prepare.R 

- CADD.indel.rda:  a R rda file contains the CADD annotations for all indels in 1000 Genome Project.

- snp.pos.txt: (example: [train/snp.pos.txt](train/snp.pos.txt)) a file with indel information "chr start end refallele and altallele" in the positve set

- snp.neg.txt: (example: [train/snp.neg.txt](train/snp.neg.txt)) a file with indel information "chr start end refallele and altallele" in the negative set

- train: the output folder
```


The output files are stored in the `train` folder, which contains five files as below

```bash
- annot.csv: (example: [train/annot.csv](train/annot.csv)), which contains CADD annotations for both positive indels and negative indels. 

- snp.pos.ref.fasta: reference genomic sequence for indels in the positve set

- snp.pos.ref.fasta: alternative genomic sequence for indels in the positve set

- snp.neg.ref.fasta: reference genomic sequence for indels in the negative set

- snp.neg.ref.fasta: alternative genomic sequence for indels in the negative set
```


We further apply the pretrained deep learning model (e.g. DanQ model) to predict 919 multi-omics features using reference/alternative genomic sequences 
The trained weights of DanQ model are provided in the `checkpoint/` directory, while the model code is present in `models/` directory. You can train your own model by using data from DeepSEA website (http://deepsea.princeton.edu/help/). 

File `src/prepare.py` calls DanQ model to predict 919 multi-omics features. You can learn more about the script arguments using the `-h` command for individual files.

```
$ python prepare.py -h
usage: prepare.py [-h] [--path PATH]

Arguments for preparing features.

options:
  -h, --help   show this help message and exit
  --path PATH  path for input data
  
Example:
python prepare.py --path ../train
python prepare.py --path ../test

``seq_features.h5" will be generated in the desired folder
```


### Train TIVAN-indel model

The model architecture is described in Figure 1 (Part C). It uses a compilation of both 45 CADD annotations and 919 multi-omics features as generated above. We call `train.py` to train the model

```bash
python train.py --path ../train --output ../res/model.json
```

### Predict

For given new indels (example: [test/snp.pos.txt](test/snp.pos.txt) and [test/snp.neg.txt](test/snp.neg.txt)), we use the aforementioned steps `predict.R` and `predict.py` to generate the input features, which will be stored in another folder `test`.  Then, we call `predict.py` to predict the functional scores.

```bash
python predict.py --path ../test --model ../res/model.json --output ../res/output.txt
```


## Obtain precomputed tissue-specific functional scores for query small indels

To make TIVAN-indel widely accessible to the research community, we provide the precomputed functional scores for all nc-sindels in 1000 Genomes Project across 44 tissues on the github webpage. With the provided R scripts on the github webpage ([R/TIVAN-indel.R](R/TIVAN-indel.R)), users can easily and quickly retrieve the functional scores for query sindels for one or multiple tissues.

### Data and code preparation

- All noncoding small indels in 1000 Genomes (sindel.noncoding.1kg.rda) can be downloaded from [here](https://drive.google.com/file/d/1u7PV9JqM1YmllutP56Gv0faP_Yhf1h4_/view?usp=share_link).

- The precomputed scores for All noncoding small indels in 1000 Genomes across 44 tissues/cell types (e.g., Adipose_Subcutaneous.score.rda) in GTEX can be downloaded from [here](https://drive.google.com/drive/folders/1fZ_V4_2sr-lPCa1HItXoUIvJ40qa_w_h?usp=share_link). The 44 tissues/cell types from GTEX are summarized in the following table.


|Tissue                                |Tissue.class  |
|:-------------------------------------|:-------------|
|Adipose_Subcutaneous                  |Adipose       |
|Adipose_Visceral_Omentum              |Adipose       |
|Adrenal_Gland                         |Adrenal Gland |
|Artery_Aorta                          |Artery        |
|Artery_Coronary                       |Artery        |
|Artery_Tibial                         |Artery        |
|Brain_Anterior_cingulate_cortex_BA24  |Brain         |
|Brain_Caudate_basal_ganglia           |Brain         |
|Brain_Cerebellar_Hemisphere           |Brain         |
|Brain_Cerebellum                      |Brain         |
|Brain_Cortex                          |Brain         |
|Brain_Frontal_Cortex_BA9              |Brain         |
|Brain_Hippocampus                     |Brain         |
|Brain_Hypothalamus                    |Brain         |
|Brain_Nucleus_accumbens_basal_ganglia |Brain         |
|Brain_Putamen_basal_ganglia           |Brain         |
|Breast_Mammary_Tissue                 |Breast        |
|Cells_EBV-transformed_lymphocytes     |Lymphocytes   |
|Cells_Transformed_fibroblasts         |Fibroblasts   |
|Colon_Sigmoid                         |Colon         |
|Colon_Transverse                      |Colon         |
|Esophagus_Gastroesophageal_Junction   |Esophagus     |
|Esophagus_Mucosa                      |Esophagus     |
|Esophagus_Muscularis                  |Esophagus     |
|Heart_Atrial_Appendage                |Heart         |
|Heart_Left_Ventricle                  |Heart         |
|Liver                                 |Liver         |
|Lung                                  |Lung          |
|Muscle_Skeletal                       |Muscle        |
|Nerve_Tibial                          |Nerve         |
|Ovary                                 |Ovary         |
|Pancreas                              |Pancreas      |
|Pituitary                             |Pituitary     |
|Prostate                              |Prostate      |
|Skin_Not_Sun_Exposed_Suprapubic       |Skin          |
|Skin_Sun_Exposed_Lower_leg            |Skin          |
|Small_Intestine_Terminal_Ileum        |Intestine     |
|Spleen                                |Spleen        |
|Stomach                               |Stomach       |
|Testis                                |Testis        |
|Thyroid                               |Thyroid       |
|Uterus                                |Uterus        |
|Vagina                                |Vagina        |
|Whole_Blood                           |Blood         |


- TIVAN-indel.R: R software to retrieve the precomputed scores for query sindels and is available at [R/TIVAN-indel.R](R/TIVAN-indel.R)

- region.txt: query regions in the following example ([example/region.txt](example/region.txt)) such as:

<img width="881" alt="Screen Shot 2022-12-31 at 4 05 17 PM" src="https://user-images.githubusercontent.com/29525389/210155683-13f95a25-415d-47ae-bcc5-30d37b92f139.png">


### Command line arguments
```r 
- Usage: R --slave --args --no-save arg1 arg2 arg3 arg4 < TIVAN-indel.R 

  - arg1: Input region: regionfile of small indels. The file has three columns "chr start end" with space/tab-delimited (chr1 10001 20000)
  - arg2: A file of all known 1000 Genome indels
  - arg3: A file/files of pre-computed score of 1000 Genome indels, multiple files are separated by comma
  - arg4: A output file contains retrieved scores for sindels in query region
```

### Examples


- Example One: Interested in one tissue at a time
```r 
R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda output.txt  < TIVAN-indel.R
```

- Example Two: Interested in multiple tissues at the same time
```r 
R --slave --args --no-save region.txt sindel.noncoding.1kg.rda Adipose_Subcutaneous.score.rda,Adipose_Visceral_Omentum.score.rda output.txt  < TIVAN-indel.R
```


The expected otuput from Example Two is:

<img width="881" alt="Screen Shot 2022-12-31 at 4 05 17 PM" src="https://user-images.githubusercontent.com/29525389/210155653-b3f622be-af92-4589-8fc1-dea9de285bda.png">


## Citation

```
@article{10.1093/bioinformatics/btad060,
    author = {Agarwal, Aman and Zhao, Fengdi and Jiang, Yuchao and Chen, Li},
    title = "{TIVAN-indel: A computational framework for annotating and predicting noncoding regulatory small insertions and deletions}",
    journal = {Bioinformatics},
    year = {2023},
    month = {01},
    issn = {1367-4811},
    doi = {10.1093/bioinformatics/btad060},
    url = {https://doi.org/10.1093/bioinformatics/btad060},
    note = {btad060},
    eprint = {https://academic.oup.com/bioinformatics/advance-article-pdf/doi/10.1093/bioinformatics/btad060/48942673/btad060.pdf},
}
```






