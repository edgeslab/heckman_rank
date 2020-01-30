import pdb
import argparse
import numpy as np
import pandas as pd

def load_clicks(file_path, dim=700):
    cols = ['qid', 'C', 'S']
    cols += ['X'+str(i+1) for i in range(dim)]

    num_lines = sum(1 for line in open(file_path))
    
    data = {}
    for c in cols:
        data[c] = np.zeros(num_lines)

    with open(file_path) as f:
        lcount = 0
        for line in f:
            tokens = line.strip().split(' ')

            data['qid'][lcount] = int(tokens[0])
            data['C'][lcount] = int(tokens[1])
            data['S'][lcount] = int(tokens[-1])
            
            for t in tokens[2:-2]:
                col = 'X' + t.split(':')[0]
                data[col][lcount] = float(t.split(':')[1])

            lcount += 1
    
    df = pd.DataFrame.from_dict(data)
    df = df.fillna(0.0)
    return df
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', default='data/test.Ragib_svm_to_anything.see10.1pass.eta1', help='data file path.')
    parser.add_argument('-o', default='data/pickles/', help='output dir for pickles.')
    parser.add_argument('-dt', default='train', help='train/test.')
    parser.add_argument('-eta', default='1.0', help='eta.')
    parser.add_argument('-fmt', default='csv', help='file format (pkl/csv).')
    args = parser.parse_args()

    df = load_clicks(args.f)
    see = args.f.split('/')[-1].split('.')[2]   # sample: naive_svm.5pass.[see19].eta2.train

    if args.fmt == 'pkl':
        df.to_pickle(args.o + '/' + args.dt + '_clicks_' + see + '_' + args.eta + '.pkl')
    elif args.fmt == 'csv':
        df.to_csv(args.o + '/' + args.dt + '_clicks_' + see + '_' + args.eta + '.csv', index=False)
    else:
        pass

if __name__ == "__main__":
    main()
