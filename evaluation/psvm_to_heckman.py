import os
import pdb
import argparse

def convert(source, target):
    target_file = open(target, 'w')
    with open(source, 'r') as source_file:
        for line in source_file:
            tokens = line.strip().split(' ')
            c = tokens[0]   
            qid = tokens[1].split(':')[-1]
            feat_offset = 3 if tokens[2].split(':')[0] == 'cost' else 2
            features = ' '.join(tokens[feat_offset:])

            line_out = '%s %s %s 0 0\n' % (qid, c, features)
            target_file.write(line_out)
    target_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', default='generated_data/svm/propensity/eta2/first_run', help='data source for svm.')
    parser.add_argument('-t', default='temp/heckman_svm_converted/eta2/first_run', help='data source for heckman.')
    parser.add_argument('-n', type=int, default='30', help='number of files to convert')
    parser.add_argument('-eta', type=str, default='2', help='eta.')
    parser.add_argument('-npass', type=int, default='5', help='eta.')
    args = parser.parse_args()



    source_file = os.path.join(args.s, 'prop_svm.%dpass.see%d.eta%s.test' % (args.npass, args.n, args.eta))
    target_file = os.path.join(args.t, 'heckman_svm.%dpass.see%d.eta%s.test' % (args.npass, args.n, args.eta))
    
    convert(source_file, target_file)


if __name__ == "__main__":
    main()
