import os
import pdb

import numpy as np
import pandas as pd

from letor_metrics import *


rank_map = {
    'heckman': 'h_rank',
    'naive-svm' : 'n_rank', 
    'prop-svm' : 's_rank', 
    'combinedw' : 'c_rank',
    'combined-agg' : 'agg_rank',
}
score_map = {
    'heckman': 'h_score',
    'prop-svm' : 's_score',
    'naive-svm' : 'n_score',
    'combinedw' : 'cw_score',
    'combined-agg' : 'ca_score',
}
pretty_map = {
    'heckman': 'Heckman',
    'prop-svm' : 'PropSVM',
    'naive-svm' : 'NaiveSVM',
    'combinedw' : 'CombinedW',
    'combined-agg' : 'RankAgg'
}


def load_svm_result(svm_pred_path, eval_data, score_name):
    with open(svm_pred_path, 'r') as svm_file:
        for name, group in eval_data.groupby(['qid']):
            num_lines = group.shape[0]

            qid = group['qid'].min()
            scores = []
            for i in range(num_lines):
                try:
                    scores.append(float(svm_file.readline().strip()))
                except:
                    print("ERROR: heckman=svm line mismatch!!")
            
            eval_data.loc[eval_data['qid'] == qid, score_name] = scores


def combine(heckman_file_path, psvm_file_path, psvm_score='s_score', nsvm_file_path='', nsvm_score='n_score'):
    eval_data = pd.read_csv(heckman_file_path)
    eval_data['qid'] = eval_data['qid'].astype(int)

    load_svm_result(psvm_file_path, eval_data, psvm_score)
    eval_data[psvm_score] = (eval_data[psvm_score] - eval_data[psvm_score].min()) / (eval_data[psvm_score].max() - eval_data[psvm_score].min())

    if nsvm_file_path != '':
        load_svm_result(nsvm_file_path, eval_data, nsvm_score)
        eval_data[nsvm_score] = (eval_data[nsvm_score] - eval_data[nsvm_score].min()) / (eval_data[nsvm_score].max() - eval_data[nsvm_score].min())

    return eval_data


def create_custom_df(name, algos, metrics):
    init_map = {
        'result'    :   'see',
        'rank'      :   'qid'      
    }

    results = {
        init_map[name] : []
    }

    for algo in algos:
        for m in metrics:
            results['%s_%s' % (algo, m)] = []

    return results


def dump_result_for_metric(df, algos, metric, pretty_map, out_file):
    out = ''.join(out_file.split('.')[:-1])    
    out_m = '%s_%s.csv' % (out, metric)
    cols = ['see']
    algo_cols = ['%s_%s' % (algo, metric) for algo in algos]
    cols += algo_cols
    result_m = df[cols].rename(columns=dict([('%s_%s' % (algo, metric), pretty_map[algo]) for algo in algos]))
    result_m.to_csv(out_m, index=False)
