import numpy as np
import xgboost as xgb
from utils import *
import argparse
import pandas as pd

np.random.seed(0)

def predict_n_save(X, args):
    # load saved model
    model = xgb.Booster()
    model.load_model(args.model)

    dtest = xgb.DMatrix(X)
    res = model.predict(dtest)

    ## save results
    df = pd.DataFrame(res, columns=['score'])
    df.to_csv(args.output, index=None, sep='\t')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for testing.'
    )
    parser.add_argument(
        '--path', default='../test/', type=str, 
        help='folder containing data'
    )
    parser.add_argument(
        '--model', default='../res/model.json', type=str, 
        help='saved model path'
    )
    parser.add_argument(
        '--output', default='../res/output.txt', type=str, 
        help='output path'
    )
    args = parser.parse_args()

    X, _ = read_features(args.path)
    predict_n_save(X, args)