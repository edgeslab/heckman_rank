dg=$1
eta=$2
run=$3
n=$4

mkdir -p data/result/
mkdir -p data/result/$dg"_eta"$eta"_"$run

printf "heckman_eta"$eta"_"$run": "

max_par=$(( $n > 14 ? 14 : $n ))

procs=0
for i in $(seq -f "%02g" 0 $max_par)
do
	python heckman.py -ds data/pickles/$dg"_eta"$eta"_"$run/ -see $i -eta $eta -o data/result/$dg"_eta"$eta"_"$run/ &
	procs=$(( $procs + 1 ))
	if [ $procs -eq 3 ];
	then
		wait
		procs=0
	fi
done
wait
echo "done"

i=$(( $max_par + 1 ))
while [ $i -le $n ]
do
	python heckman.py -ds data/pickles/$dg"_eta"$eta"_"$run/ -see $i -eta $eta -o data/result/$dg"_eta"$eta"_"$run/
    i=$(( $i + 1 ))
done

