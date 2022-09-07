import numpy as np
import h5py, json
import xgboost as xgb
from utils import *

nFolds = 5
tissue = 'CD4_NAIVE'

model = xgb.Booster()
model.load_model(f'../res/Whole_Blood.json')

np.random.seed(0)

hf = h5py.File(f'../data/{tissue}.h5', 'r')
ref = np.array(hf['feat_ref'])
alt = np.array(hf['feat_alt'])
annot = np.array(hf['annot'])
label = np.array(hf['label'])
hf.close()

X = np.hstack([annot, ref, alt])

dtest = xgb.DMatrix(norm(X), label=label)
res = model.predict(dtest)

stats = get_stats(label, res)
with open(f'../res/{tissue}_test.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=4)