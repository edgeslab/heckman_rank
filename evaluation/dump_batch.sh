ds=$1
eta=$2
npass=$3
out=$4
n=$5

njobs=4

procs=0
for seen in $(seq 0 $n);
do
	python dump_df.py -f $ds"/heckman_svm."$npass"pass.see"$seen".eta"$eta".train" -o $out -dt train -eta $eta &
    	echo "train done "$seen
	
	procs=$(( $procs + 1 ))
	if [ $procs -eq $njobs ];
	then
		wait
		procs=0
	fi
done
wait

procs=0
for seen in $(seq 0 $n);
do
	python dump_df.py -f $ds"/heckman_svm."$npass"pass.see"$seen".eta"$eta".test" -o $out -dt test -eta $eta &
    	echo "test done "$seen

	if [ $procs -eq $njobs ];
	then
		wait
		procs=0
	fi
done
wait

