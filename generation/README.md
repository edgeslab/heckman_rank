The svm.py generates semisynthetic data, when base ranker is naive-svm. To run this code, use python2, along with the follwing arguments

argument 1: 99% of train data in set1 of Yahoo! learning-to-rank dataset
argument 2: prediction file that contains base ranker scores for 99% of train data
argument 3: output file address in which naive-svm data will be written in
argument 4: output file address in which propensity-svm data will be written in
argument 5: output file address in which heckmanRank data will be written in
argument 6: number of passes or sampling times, which is 5 in our results
argument 7: cut off (k), which is 0-29
argument 8: eta or severity of position bias (0, 0.5, 1, 1.5 and 2 in our results)
