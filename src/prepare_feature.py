import os
import h5py
import pandas as pd
import numpy as np
import argparse

import sys
sys.path.append('../')
from models.DanQ import DanQ

SEQ_LENGTH = 1000                                                               # sequence length accepted by DanQ model

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
def prepare_sequence(model, path):
    neg_filename = path
    pos_filename = path.replace('neg', 'pos')
    seq = np.vstack(
        [get_sequence(pos_filename), get_sequence(neg_filename)]
    )[:, :SEQ_LENGTH]

    return model.predict(seq)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for preparing features.'
    )
    parser.add_argument(
        '--path', default='../data/', type=str, help='base path for input data'
    )
    parser.add_argument(
        '--tissue', default='CD4_NAIVE', type=str, help='tissue name'
    )
    args = parser.parse_args()

    # prepare input features
    file_path = os.path.join(args.path, f'{args.tissue}.annot.csv')
    annot = prepare_annotations(file_path)

    danQ = DanQ(name='DanQ')
    ref_path = os.path.join(args.path, f'{args.tissue}.neg.ref.fasta')
    ref = prepare_sequence(danQ, path=ref_path)
    alt_path = os.path.join(args.path, f'{args.tissue}.neg.alt.fasta')
    alt = prepare_sequence(danQ, path=alt_path)

    # prepare labels
    size = len(annot)
    label = np.zeros(size)
    label[:size//2] = 1
    label = label.reshape(-1, 1).astype('uint8')

    # save everything in one h5 file
    file_path = os.path.join(args.path, f'{args.tissue}.h5')
    hf = h5py.File(file_path, 'w')
    hf.create_dataset('feat_ref', data=ref)
    hf.create_dataset('feat_alt', data=alt)
    hf.create_dataset('label', data=label)
    hf.create_dataset('annot', data=annot)
    hf.close()