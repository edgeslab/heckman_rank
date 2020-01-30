#!/bin/bash

eta=$1
pass=$2
n=$3

dg="svm"
out="results/"$pass"pass_eta"$eta"_combined.csv"

mkdir -p plots
mkdir -p results

STARTTIME=$(date +%s)
MINUTES=60

sh nsvm_rank.sh generated_data/svm/naive $eta $pass "nsvm_results/svm_eta"$eta"_first/" $n > /dev/null 
echo "evaluating naive svm ... done"

sh psvm_rank.sh generated_data/svm/propensity $eta $pass "psvm_results/svm_eta"$eta"_first/" $n > /dev/null 
echo "evaluating prop svm ... done"

sh convert.sh  $eta $pass $n "generated_data/svm/propensity/eta"$eta"/first_run/" "generated_data/heckman_svm/eta"$eta"/first_run" > /dev/null
echo "converting prop svm test files to heckman test files ... done"

sh dump_batch_3.sh generated_data/heckman_svm/ $eta svm $pass $n > /dev/null
echo "dumping heckman svm train and test files ... done"

sh heckman_eval_eta.sh $dg $eta first $n > /dev/null
echo "evaluating heckman ... done"

python combine.py -hr "data/result/svm_eta"$eta"_first" -pr "psvm_results/svm_eta"$eta"_first" -nr "nsvm_results/svm_eta"$eta"_first" -n $n -eta $eta -out $out
echo "combining ranks ... done"

python plotter.py -res "results/"$pass"pass_eta"$eta"_combined_arrr.csv" -out "plots/"$pass"pass_eta"$eta"_combined_arrr.eps"
python plotter.py -res "results/"$pass"pass_eta"$eta"_combined_ndcg_10.csv" -out "plots/"$pass"pass_eta"$eta"_combined_ndcg_10.eps"

ENDTIME=$(date +%s)
elapsed=`echo "("$ENDTIME - $STARTTIME")/"$MINUTES | bc -l | xargs printf %.2f`
echo "done in ["$elapsed"] minutes!"

