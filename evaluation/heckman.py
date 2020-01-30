import os
import pdb
import argparse
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

def warn(*args, **kwargs):
    pass
warnings.warn = warn

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm
# import statsmodels.api as sm



pd.options.mode.chained_assignment = None

def probit(Y, X):   
    clf = LogisticRegression(solver='lbfgs').fit(X, Y)
    return clf.coef_/1.6


def inverse_mills(val):
    return norm.pdf(val) / norm.cdf(val)


def read_data(data_file, file_format='csv'):
    if file_format == 'csv':
        return pd.read_csv(data_file)
    
    if file_format == 'pkl':
        return pd.read_pickle(data_file)
    
    return None


def heckman(train):
    X = train[train.columns.drop(['qid', 'C', 'S'])]
    Y = train['S']

    gamma = probit(Y, X).T
    lambda_ = inverse_mills(np.matmul(X, gamma))
    
    Y = train['C']
    params = probit(Y, np.append(X, lambda_.reshape(-1,1), 1))
    lam_coeff= params[0][-1]
    x_coeff= params[0][0:-1]
    
    return x_coeff


def eval(df, params, score_name='h_score'):
    X_test = df[df.columns.drop(['qid', 'C', 'S'])]
    Eval = df[['qid', 'C']]

    Eval[score_name] = norm.cdf(np.matmul(X_test, params))
    
    return Eval


def eval_out(df, params, score_name, out_file):
    eval_data = eval(df, params, score_name='h_score')
    eval_data['h_score'] = (eval_data['h_score'] - eval_data['h_score'].min()) / (eval_data['h_score'].max() - eval_data['h_score'].min())
    eval_data.to_csv(out_file, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ds', default='data/pickles/pop_eta0_first/', help='pickle data source.')
    parser.add_argument('-fmt', default='csv', help='data file format.')
    parser.add_argument('-see', type=int, default='0', help='see threshold.')
    parser.add_argument('-eta', type=str, default='0', help='eta.')
    parser.add_argument('-o', default='data/result/', help='output directory path')
    args = parser.parse_args()

    # Load train file into dataframe
    train_file = os.path.join(args.ds, 'train_clicks_see%d_%s.%s' % (args.see, args.eta, args.fmt))
    train = read_data(train_file, args.fmt)
    
    train['S'] = train['S'].astype(int)
    train['C'] = train['C'].astype(int)

    # Load test file into dataframe
    test_file = os.path.join(args.ds, 'test_clicks_see%d_%s.%s' % (args.see, args.eta, args.fmt))
    test = read_data(test_file, args.fmt)
    test['C'] = test['C'].astype(int)

    # Learn params through Heckman method
    params = heckman(train)

    # Evaluate train data 
    out_train_file = os.path.join(args.o, 'train_scores_see%d_%s.csv' % (args.see, args.eta))
    eval_out(train, params, score_name='h_score', out_file=out_train_file)
    
    # Evaluate test data 
    out_test_file = os.path.join(args.o, 'test_scores_see%d_%s.csv' % (args.see, args.eta))
    eval_out(test, params, score_name='h_score', out_file=out_test_file)

    




if __name__ == "__main__":
    main()