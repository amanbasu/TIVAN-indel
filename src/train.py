import numpy as np
import xgboost as xgb
from utils import *
import argparse

def train_n_save(X, label, args):

    np.random.seed(0)

    # parameters abtained after hyperparameter tuning
    params = {
        'colsample_bytree': 0.35, 
        'gamma': 0.87, 
        'learning_rate': 0.01, 
        'max_depth': 10, 
        'n_estimators': 400, 
        'reg_alpha': 0.87, 
        'subsample': 1
    }

    clf = xgb.XGBClassifier(**params,
        objective='binary:logistic',
        seed=0,
        use_label_encoder=False,
        eval_metric='logloss')
    clf.fit(X, label)
    clf.save_model(args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Arguments for training.'
    )
    parser.add_argument(
        '--path', default='../train/', type=str, 
        help='input data folder'
    )
    parser.add_argument(
        '--output', default='../res/model.json', type=str, 
        help='path of saved xgb model after training'
    )
    args = parser.parse_args()

    X, y = read_features(args.path)
    train_n_save(X, y, args)
