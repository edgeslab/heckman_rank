ds=$1
eta=$2
name=$3
npass=$4
n=$5

mkdir -p "data/pickles/"$name"_eta"$eta"_first/"
sh dump_batch.sh $ds"/eta"$eta"/first_run/" $eta $npass "data/pickles/"$name"_eta"$eta"_first/" $n
wait
echo "first run done"

# mkdir -p "data/pickles/"$name"_eta"$eta"_second/"
# sh dump_batch.sh $ds"/eta"$eta"/second_run/" $eta "data/pickles/"$name"_eta"$eta"_second/"
# wait
# echo "second run done"

# mkdir -p "data/pickles/"$name"_eta"$eta"_third/"
# sh dump_batch.sh $ds"/eta"$eta"/third_run/" $eta "data/pickles/"$name"_eta"$eta"_third/"
# echo "third run done"
