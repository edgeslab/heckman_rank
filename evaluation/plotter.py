import pdb
import argparse

import matplotlib
import pandas as pd

from sys import platform

if platform == "darwin":    
    matplotlib.use('TkAgg')
else:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt

def plot_init(fsize, xlabel, ylabel):
    plt.figure(figsize=(16,12))
    plt.rc('legend', fontsize=fsize)
    plt.rc('xtick',labelsize=fsize)
    plt.rc('ytick',labelsize=fsize)
    plt.rcParams["font.family"] = "Times New Roman"

    plt.xlabel(xlabel, fontsize=fsize+10)
    plt.ylabel(ylabel, fontsize=fsize+10)
    

def draw_multi_y_column(df, num_plots, labels, xlabel, ylabel, filename, fmt='eps'):
    columns = list(df.columns)
    
    xcol = columns[0]
    ycols = columns[1:]

    # TODO: clean up this part
    ycols[2], ycols[3] = ycols[3], ycols[2]
    # labels[2], labels[3] = labels[3], labels[2]

    plot_init(fsize=32, xlabel=xlabel, ylabel=ylabel)
    
    legend_handles = []
    linestyles = ['-', '-', '-', '-', '-']
    markers = ["o", "^", "s", "P", "D"]
    colors = ['blue', 'green', 'gold', 'red', 'purple']
    ls = 0
    for i in range(num_plots):
        # df[xcols[i]] = df[xcols[i]] * 60
        line, = plt.plot(xcol, ycols[i], data=df, linewidth=3, linestyle=linestyles[ls], color=colors[ls], marker=markers[ls], markersize=12)
        legend_handles.append(line)
        ls += 1

    legend_handles[2], legend_handles[3] = legend_handles[3], legend_handles[2]

    metric_suffix = filename.split('.')[-2].split('_')[-1]
    is_noisy = filename.split('_')[0] == 'noisy'
    eta = filename.split('_')[2]

    axes = plt.gca()
    if metric_suffix == 'arrr':
        axes.set_ylim([4.5,11.5])       # for set2
        # axes.set_ylim([11,13.5])      # fro set1
    elif metric_suffix == 'mrr1':
        axes.set_ylim([0.2,0.45])
    else:
        axes.set_ylim([0.25,0.55])      # for set2
        # axes.set_ylim([0.28,0.41])    # for set1

    if is_noisy and eta == 'eta15':
        legend_loc = 'lower right' if metric_suffix == 'arrr' else 'upper right'  
    else:
        legend_loc = 'upper right' if metric_suffix == 'arrr' else 'lower right'

    plt.legend(handles=legend_handles, labels=labels, loc=legend_loc, prop={'size': 32}, ncol=2)

    if fmt == 'eps':
        plt.savefig(filename, format='eps', dpi=2000, bbox_inches='tight')
    else:
        plt.savefig(filename, format=fmt, bbox_inches='tight')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-res', default='15_pass_eta1_combinedw_arrr.csv', help='combined result file.')
    parser.add_argument('-out', default='', help='output image filename.')
    parser.add_argument('-fmt', default='eps', help='image format.')
    args = parser.parse_args()

    results = pd.read_csv(args.res)
    metric_suffix = args.res.split('.')[-2].split('_')[-1]

    xlabel = 'Number of observed documents(k)'
    ylabel = ''
    
    if metric_suffix == 'arrr':
        ylabel = 'Average Rank of Relevant Result'
    elif metric_suffix == 'mrr1':
        ylabel = 'Mean Reciprocal Rank'
    else:
        ylabel = 'nDCG@10'

    out_file = args.out
    if out_file == '':
        out_file = '%s.%s' % (''.join(args.res.split('.')[:-1]), args.fmt)
    draw_multi_y_column(results, results.shape[1]-1, list(results.columns.drop(['see'])), xlabel, ylabel, out_file, fmt=args.fmt)


if __name__ == "__main__":
    main()