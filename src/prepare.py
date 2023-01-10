import os
import h5py
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

# get 919 features from DanQ model
def prepare_sequence(model, args, type='ref'):
    pos_filename = os.path.join(args.path, f'snp.pos.{type}.fasta')
    neg_filename = os.path.join(args.path, f'snp.neg.{type}.fasta')
    
    pos_seq = get_sequence(pos_filename)
    neg_seq = get_sequence(neg_filename)

    seq = np.vstack([pos_seq, neg_seq])[:, :SEQ_LENGTH]

    label = np.zeros(len(seq))
    label[:len(pos_seq)] = 1

    return model.predict(seq), label

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for preparing features.'
    )
    parser.add_argument(
        '--path', default='../train/', type=str, help='path for input data'
    )
    args = parser.parse_args()

    # prepare input features
    danQ = DanQ(name='DanQ')
    ref, label = prepare_sequence(danQ, args, type='ref')
    alt, _ = prepare_sequence(danQ, args, type='alt')

    # prepare labels
    label = label.reshape(-1, 1).astype('uint8')

    # save everything in one h5 file
    file_path = os.path.join(args.path, 'seq_features.h5')
    hf = h5py.File(file_path, 'w')
    hf.create_dataset('feat_ref', data=ref)
    hf.create_dataset('feat_alt', data=alt)
    hf.create_dataset('label', data=label)
    hf.close()