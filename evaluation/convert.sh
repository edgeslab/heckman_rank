
eta=$1
pass=$2
n=$3
source=$4
target=$5

for i in $(seq -f "%g" 0 $n)
do
	python psvm_to_heckman.py -s $source -t $target -n $i -eta $eta -npass $pass &
done
wait

echo "convert done"
