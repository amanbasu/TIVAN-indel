import os
import h5py
import pandas as pd
import numpy as np

import sys
sys.path.append('../')
from models.DanQ import DanQ

seq_length = 1000
base_path = '../data/'
tissue = 'CD4_NAIVE'
csv_file = '{base_path}{tissue}.annot_pos.csv'

def one_hot(x):
    arr = np.array(list(x))
    a = (arr == 'A')
    g = (arr == 'G')
    c = (arr == 'C')
    t = (arr == 'T')
    return np.vstack([a, g, c, t]).T

def get_sequence(filename):
    with open(filename, 'r') as f:
        seq = f.read()
        
    seq = seq.replace('\n', '').split('>')[1:]
    seq = list(map(one_hot, seq))
    seq = np.array(seq).astype('uint8')
    return seq

def get_annotations(fname):
    df_pos = pd.read_csv(fname)
    os.remove(fname)
    df_neg = pd.read_csv(fname.replace('pos', 'neg'))
    os.remove(fname.replace('pos', 'neg'))

    annot = pd.concat([df_pos, df_neg])
    annot.reset_index(drop=True, inplace=True)
    annot.drop(columns=['RawScore', 'PHRED'], inplace=True)

    return annot

def get_sequence(model, type='ref'):
    neg_filename = base_path + f'{tissue}.neg.{type}.fasta'
    pos_filename = base_path + f'{tissue}.pos.{type}.fasta'

    seq = np.vstack([get_sequence(pos_filename), get_sequence(neg_filename)])[:, :seq_length]
    return model.predict(seq)

annot = get_annotations(csv_file)

danQ = DanQ(name='DanQ')
ref = get_sequence(danQ, type='ref')
alt = get_sequence(danQ, type='alt')

size = annot.shape[0]
label = np.zeros(size)
label[:size//2] = 1
label = label.reshape(-1, 1).astype('uint8')

hf = h5py.File(f'{base_path}{tissue}.h5', 'w')
hf.create_dataset('feat_ref', data=ref)
hf.create_dataset('feat_alt', data=alt)
hf.create_dataset('label', data=label)
hf.create_dataset('annot', data=annot.iloc[:, :-1])
hf.close()