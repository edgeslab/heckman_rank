ds=$1		# generated_data/svm/propensity
ETA=$2		# 2
pass=$3		# 5
out=$4		# psvm_results/svm_eta2_first
n=$5        # Max see cutoff to run for from 0

mkdir -p psvm_results
mkdir -p temp
mkdir -p $out

for i in $(seq -f "%g" 0 $n)
do
    echo "train "$i
    svm_proprank/svm_proprank_learn -c 0.01 $ds'/eta'$ETA'/first_run/prop_svm.'$pass'pass.see'$i'.eta'$ETA'.train' 'temp/model'$i > /dev/null &
done
wait

for i in $(seq -f "%g" 0 $n)
do
    echo "predict train "$i
    svm_proprank/svm_proprank_classify $ds'/eta'$ETA'/first_run/prop_svm.'$pass'pass.see'$i'.eta'$ETA'.train' 'temp/model'$i $out'/prediction_train_see'$i'.txt' > /dev/null &
done
wait

for i in $(seq -f "%g" 0 $n)
do
    echo "predict test "$i
    svm_proprank/svm_proprank_classify $ds'/eta'$ETA'/first_run/prop_svm.'$pass'pass.see'$i'.eta'$ETA'.test' 'temp/model'$i $out'/prediction_test_see'$i'.txt' > /dev/null &
done
wait

echo "done"
