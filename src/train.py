import numpy as np
import json
import xgboost as xgb
from utils import *
import argparse

def train_n_save(X, label, args):
    # divide data for k-fold
    size = len(label)
    index_p = np.where(label==1)[0].tolist()
    index_n = np.where(label==0)[0].tolist()

    np.random.seed(0)
    np.random.shuffle(index_p)
    np.random.shuffle(index_n)

    span_p = len(index_p) // args.folds
    span_n = len(index_n) // args.folds

    labs, preds = [], []
    for fold in range(args.folds):
        print(f'Fold {fold+1}/{args.folds}')

        # prevent samples from being left out
        fend = (fold+1)*span_p
        test_p = index_p[fold*span_p:fend]
        if len(index_p) - fend < args.folds:
            test_p = index_p[fold*span_p:]

        fend = (fold+1)*span_n
        test_n = index_n[fold*span_n:fend]
        if len(index_n) - fend < args.folds:
            test_n = index_n[fold*span_n:]

        train_p = [e for e in index_p if e not in test_p]
        train_n = [e for e in index_n if e not in test_n]

        train_idx, test_idx = [*train_p, *train_n], [*test_p, *test_n]
            
        x_train = X[train_idx]
        y_train = label[train_idx]
        x_test = X[test_idx]
        y_test = label[test_idx]

        # train XGB model
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

    if args.save_model:
        bst.save_model(f'../res/{args.train_tissue}.json')
    stats = get_stats(np.array(labs).reshape(-1, 1), np.array(preds).reshape(-1, 1))
    print(stats)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for training.'
    )
    parser.add_argument(
        '--train_tissue', default='Whole_Blood', type=str, 
        help='tissue to be used for training'
    )
    parser.add_argument(
        '--folds', default=5, type=int, 
        help='number of folds to run'
    )
    parser.add_argument(
        '--save_model', default=True, type=bool, 
        help='saves xgb model if true'
    )
    args = parser.parse_args()

    X, y = read_features(args.train_tissue)
    train_n_save(X, y, args)
