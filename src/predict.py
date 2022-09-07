import numpy as np
import json
import xgboost as xgb
from utils import *
import argparse

np.random.seed(0)

tissue = 'CD4_NAIVE'

def predict_n_save(X, y, args):
    # load saved model
    model = xgb.Booster()
    model.load_model(f'../res/{args.train_tissue}.json')

    dtest = xgb.DMatrix(X, label=y)
    res = model.predict(dtest)

    stats = get_stats(y, res)
    with open(f'../res/{args.test_tissue}_test.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for testing.'
    )
    parser.add_argument(
        '--train_tissue', default='Whole_Blood', type=str, 
        help='tissue for which the model is trained on'
    )
    parser.add_argument(
        '--test_tissue', default='CD4_NAIVE', type=str, 
        help='tissue to be used for testing'
    )
    args = parser.parse_args()

    X, y = read_features(args.test_tissue)
    predict_n_save(X, y, args)