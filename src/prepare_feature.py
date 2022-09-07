import os
import h5py
import pandas as pd
import numpy as np

import sys
sys.path.append('../')
from models.DanQ import DanQ

seq_length = 1000                                                               # sequence length accepted by DanQ model
base_path = '../data/'
tissue = 'CD4_NAIVE'
csv_file = f'{base_path}{tissue}.annot.csv'

# to one-hot encode sequence features according to DanQ's input
def one_hot(x):
    arr = np.array(list(x))
    a = (arr == 'A')
    g = (arr == 'G')
    c = (arr == 'C')
    t = (arr == 'T')

    return np.vstack([a, g, c, t]).T

# read and format sequence
def get_sequence(filename):
    with open(filename, 'r') as f:
        seq = f.read()
        
    seq = seq.replace('\n', '').split('>')[1:]
    seq = list(map(one_hot, seq))
    seq = np.array(seq).astype('uint8')
    return seq

# drop un-used columns from annotations
def prepare_annotations(fname):
    df = pd.read_csv(fname)
    df.reset_index(drop=True, inplace=True)
    df.drop(columns=['RawScore', 'PHRED'], inplace=True)

    return df

# get 919 features from DanQ model
def prepare_sequence(model, type='ref'):
    neg_filename = base_path + f'{tissue}.neg.{type}.fasta'
    pos_filename = base_path + f'{tissue}.pos.{type}.fasta'
    seq = np.vstack([get_sequence(pos_filename), get_sequence(neg_filename)])[:, :seq_length]

    return model.predict(seq)

annot = prepare_annotations(csv_file)

danQ = DanQ(name='DanQ')
ref = prepare_sequence(danQ, type='ref')
alt = prepare_sequence(danQ, type='alt')

# prepare labels
size = len(annot)
label = np.zeros(size)
label[:size//2] = 1
label = label.reshape(-1, 1).astype('uint8')

# save everything in one h5 file
hf = h5py.File(f'{base_path}{tissue}.h5', 'w')
hf.create_dataset('feat_ref', data=ref)
hf.create_dataset('feat_alt', data=alt)
hf.create_dataset('label', data=label)
hf.create_dataset('annot', data=annot)
hf.close()