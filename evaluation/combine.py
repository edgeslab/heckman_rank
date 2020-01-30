import os
import pdb
import argparse

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from pyrankagg.rankagg import FullListRankAggregator

from combine_utils import *


metric_map = {
    'arrr'      :   lambda rel, rank: (rank[rel.astype(bool)]-1).mean(),
    'mrr1'      :   lambda rel, rank: 1/(rank[rel.astype(bool)].mean()),
    'mrr2'      :   lambda rel, rank: 1/(rank[rel.astype(bool)].mean() ** 2),
    'ndcg_3'    :   lambda rel, rank: ndcg_from_ranking(rel, np.argsort(rank), k=3),
    'ndcg_5'    :   lambda rel, rank: ndcg_from_ranking(rel, np.argsort(rank), k=5),
    'ndcg_7'    :   lambda rel, rank: ndcg_from_ranking(rel, np.argsort(rank), k=7),
    'ndcg_10'   :   lambda rel, rank: ndcg_from_ranking(rel, np.argsort(rank), k=10)
}



def rank(df, algos):
    for name, group in df.groupby(['qid']):
        qid = group['qid'].min()
        for algo in algos:
            df.loc[df['qid'] == qid, rank_map[algo]] = group[score_map[algo]].rank(ascending=False).astype(int)
    return df


def evaluate(df, algos, metrics):
    results = create_custom_df('rank', algos, metrics)

    for name, group in df.groupby(['qid']):
        qid = group['qid'].min()

        for algo in algos:
            df.loc[df['qid'] == qid, rank_map[algo]] = group[score_map[algo]].rank(ascending=False).astype(int)

        df_qid = df[df['qid'] == qid]
        results['qid'].append(qid)

        for m in metrics:
            for algo in algos:
                rel = np.asarray(df_qid['C'])
                rank = np.asarray(df_qid[rank_map[algo]])
                res = metric_map[m](rel, rank)
                results['%s_%s' % (algo, m)].append(res)

    result_df = pd.DataFrame.from_dict(results)

    return result_df


def combine_weight(eval_data_train, eval_data_test, X_cols, Y_col):
    X_train = eval_data_train[X_cols]
    Y_train = eval_data_train['C']
    clf = LogisticRegression(solver='lbfgs', class_weight='balanced').fit(X_train, Y_train)
    
    X_test = eval_data_test[X_cols]
    return clf.predict_proba(X_test)[:, 1]


def rank_aggregate(eval_data_train, eval_data_test, X_cols, Y_col):
    df = eval_data_test.copy()
    df['rank_agg'] = np.zeros(eval_data_test.shape[0])
    FLRA = FullListRankAggregator()
    for name, group in df.groupby(['qid']):
        qid = group['qid'].min()

        rank_dicts = []
        for algo_rank in X_cols:
            rank_dicts.append(df.loc[df['qid'] == qid, algo_rank].to_dict())

        com_ranks = FLRA.aggregate_ranks(rank_dicts, areScores=False)
        com_ranks = pd.DataFrame.from_dict(com_ranks, orient='index')[0]
        df.loc[df['qid'] == qid, 'rank_agg'] = com_ranks.astype(int)
    
    return -df['rank_agg']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-hr', default='data/result/svm_eta2_first', help='heckman results csv.')
    parser.add_argument('-pr', default='psvm_results/svm_eta2_first', help='predicrions from psvm.')
    parser.add_argument('-nr', default='nsvm_results/svm_eta2_first', help='predicrions from psvm.')
    parser.add_argument('-n', type=int, default='29', help='max threshold to combine')
    parser.add_argument('-eta', type=str, default='2', help='eta.')
    parser.add_argument('-out', default='results/10_pass_combined_eta2_first.csv', help='combined results csv.')
    args = parser.parse_args()

    metrics = ['arrr', 'mrr1', 'ndcg_10']
    algos = ['naive-svm', 'prop-svm', 'heckman']
    algos_to_combine = ['prop-svm', 'heckman']
    combine_methods = ['combinedw', 'combined-agg']
    combine_map = {'combinedw' : combine_weight, 'combined-agg': rank_aggregate}

    results = create_custom_df('result', algos + combine_methods, metrics)

    for i in range(args.n+1):
        print('combining see %d' % i)
        try:
            # Load training scores and combine   
            file_heckman_train_result = os.path.join(args.hr, 'train_scores_see%d_%s.csv' % (i, args.eta))
            file_psvm_train_result = os.path.join(args.pr, 'prediction_train_see%d.txt' % (i))
            eval_data_train = combine(file_heckman_train_result, file_psvm_train_result, 's_score')
            eval_data_train = rank(eval_data_train, algos_to_combine)

            # Load test scores and combine
            file_heckman_test_result = os.path.join(args.hr, 'test_scores_see%d_%s.csv' % (i, args.eta))
            file_psvm_test_result = os.path.join(args.pr, 'prediction_test_see%d.txt' % (i))
            file_nsvm_test_result = os.path.join(args.nr, 'naive_prediction_test_see%d.txt' % (i))
            eval_data_test = combine(file_heckman_test_result, file_psvm_test_result, 's_score', file_nsvm_test_result, 'n_score')
            eval_data_test = rank(eval_data_test, algos)
        except:
            continue

        # Predict on test scores
        X_cols = [rank_map[algo] for algo in algos_to_combine]

        for comb_name in combine_methods:
            comb_method = combine_map[comb_name]
            eval_data_test[score_map[comb_name]] = comb_method(eval_data_train, eval_data_test, X_cols, 'C')

        # generate ranking based on final score
        all_algos = algos + combine_methods
        result_df = evaluate(eval_data_test, all_algos, metrics)

        results['see'].append(i)
        for m in metrics:
            for algo in (all_algos):
                algo_m = '%s_%s' % (algo, m)
                results[algo_m].append(result_df[algo_m].mean())

    df = pd.DataFrame.from_dict(results)

    for m in metrics:
        dump_result_for_metric(df, all_algos, m, pretty_map, args.out)



if __name__ == "__main__":
    main()
