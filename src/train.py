import numpy as np
import h5py, json
import xgboost as xgb
from utils import *

nFolds = 5
tissue = 'Whole_Blood'

hf = h5py.File(f'../data/{tissue}.h5', 'r')
ref = np.array(hf['feat_ref'])
alt = np.array(hf['feat_alt'])
annot = np.array(hf['annot'])
label = np.array(hf['label'])
hf.close()

X = np.hstack([annot, ref, alt])
X = norm(X)

size = len(label)
index_p = np.where(label==1)[0].tolist()
index_n = np.where(label==0)[0].tolist()

np.random.seed(0)
np.random.shuffle(index_p)
np.random.shuffle(index_n)

span_p = len(index_p) // nFolds
span_n = len(index_n) // nFolds

labs, preds, indx = [], [], []
for fold in range(nFolds):
    print(f'Fold {fold+1}/{nFolds}')

    # prevent samples from being left out
    fend = (fold+1)*span_p
    test_p = index_p[fold*span_p:fend]
    if len(index_p) - fend < nFolds:
        test_p = index_p[fold*span_p:]

    fend = (fold+1)*span_n
    test_n = index_n[fold*span_n:fend]
    if len(index_n) - fend < nFolds:
        test_n = index_n[fold*span_n:]

    train_p = [e for e in index_p if e not in test_p]
    train_n = [e for e in index_n if e not in test_n]

    train_idx, test_idx = [*train_p, *train_n], [*test_p, *test_n]
        
    x_train = X[train_idx]
    y_train = label[train_idx]
    x_test = X[test_idx]
    y_test = label[test_idx]

    dtrain = xgb.DMatrix(x_train, label=y_train)
    dtest = xgb.DMatrix(x_test, label=y_test)
    evallist = [(dtrain, 'train'), (dtest, 'eval')]
    params = {
        'max_depth': 3, 
        'objective': 'binary:logistic', 
        'max_delta_step': 1,
        'eta': 0.1, 
        'nthread': 4, 
        'eval_metric': ['aucpr', 'map'], 
        'seed': fold
    }
    bst = xgb.train(params, dtrain, 100, evallist, 
        early_stopping_rounds=20, verbose_eval=False
    )
    res = bst.predict(dtest)
    preds += list(res)
    labs += list(y_test)

bst.save_model(f'../res/{tissue}.json')
stats = get_stats(np.array(labs).reshape(-1, 1), np.array(preds).reshape(-1, 1))
with open(f'../res/{tissue}_stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=4)
