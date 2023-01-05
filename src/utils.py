from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import numpy as np
import h5py
import os
import pandas as pd

def get_stats(y, y_hat):
    # get area under the curve (auc) score
    auroc = roc_auc_score(y, y_hat)

    precision, recall, _ = precision_recall_curve(y, y_hat)
    auprc = auc(recall, precision)

    return {'auroc': auroc, 'auprc': auprc}

def read_features(path):
    hf_fname = os.path.join(path, 'seq_features.h5')
    hf = h5py.File(hf_fname, 'r')

    ref = np.array(hf['feat_ref'])
    alt = np.array(hf['feat_alt'])
    label = np.array(hf['label'])
    hf.close()

    annot_fname = os.path.join(path, 'annot.csv')
    annot = pd.read_csv(annot_fname)
    annot.reset_index(drop=True, inplace=True)
    annot.drop(columns=['RawScore', 'PHRED'], inplace=True)

    X = np.hstack([annot, ref, alt])

    return X, label