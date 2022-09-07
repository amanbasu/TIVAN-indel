from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import numpy as np
import h5py

def get_stats(y, y_hat):
    # get area under the curve (auc) score
    auroc = roc_auc_score(y, y_hat)

    precision, recall, _ = precision_recall_curve(y, y_hat)
    auprc = auc(recall, precision)

    return {'auroc': auroc, 'auprc': auprc}

def norm(x):
    return (x - np.min(x, axis=0)) / (np.max(x, axis=0) - np.min(x, axis=0))

def read_features(tissue):
    hf = h5py.File(f'../data/{tissue}.h5', 'r')
    ref = np.array(hf['feat_ref'])
    alt = np.array(hf['feat_alt'])
    annot = np.array(hf['annot'])
    label = np.array(hf['label'])
    hf.close()

    X = np.hstack([annot, ref, alt])
    X = norm(X)

    return X, label