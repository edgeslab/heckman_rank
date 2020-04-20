

#This code generate data when base ranker is SVM-rank, the process is as follows: 
#Base ranker learn o 1% of data, and generates a prediction score for the remaining 99% of data
#The 99% of data will be ranked according to the prediction score
#clicks will be generated from this ranked data with multiple sampling times (multiple pass) to augment data
# The final generated data will be written to be fed into naive svm, propensity svm and heckman


import random,operator,numpy as np
from copy import deepcopy
import sys

class searchItem:

    def __init__(self , r , t, a):
        self.true_rel=t
        self.ranking=r
        self.attributes=a


class searchResult:

    def __init__(self):
        self.result = []
        self.clicked = {}

    def sortByRank(self):
        
        self.result.sort(key = operator.attrgetter('ranking'), reverse = True)          
        for i in range(len(self.result)):
            self.result[i].ranking = i

    def doPrint(self):
        print "searchResult"
        for r in self.result:
            print "ranking=" + str(r.ranking) + ", true_rel=" + str(r.true_rel) + ", att=" + str(r.attributes)
        print "============"

    def getRankOfClicked(self, clicks):
        counter = 0
        r=[]
        # assert len(clicks) == len(self.result)
        for c in clicks:
            assert c==0 or c==1
            if c==1:
                r.append(self.result[counter].ranking)

            counter = counter+1

        return r


    def setPropencityScores(self, clicks, eta):
        counter = 0
        r=[]
        # assert len(clicks) == len(self.result)
        for c in clicks:
            assert c==0 or c==1
            if c==1:
                p = 1/((1/(1+float(self.result[counter].ranking)))**eta)
                self.clicked[counter] = p
            counter = counter+1



    def gen_clicks(self, eta):

        # assert len(self.ranking) == len(self.true_rel)
        count = len(self.result)
        '''
            count       = number of documents in search result (for a single query)
            ranking     = ranking of the documents in search result
            relevance   = true relevance of the documents provided in data
            eta         = presentation bias factor
        '''

#@@@@@@@@@START: noisy click, comment out for noiseless@@@@@@@@@#
        #eneg = 0.4
        #for i in range(count):
            #if self.result[i].true_rel < 1:  # docs with rel=0, will have rel=0.1#
                #assert (self.result[i].true_rel == 0)
                #self.result[i].true_rel = eneg
#@@@@@@@@@END: noisy click, comment out for noiseless@@@@@@@@@#


        exam_prob = np.zeros(count)  # examination probability
        click_prob = np.zeros(count)  # click probability
        clicks = np.zeros(count, dtype=np.int)  # actual clicks

        for i in range(count):
            doc_i = self.result[i].ranking
            exam_prob[doc_i] = (1.0 / (i + 1)) ** eta
            click_prob[doc_i] = exam_prob[doc_i] * self.result[doc_i].true_rel

        if np.sum(
                click_prob) <= 0:                                         # if no probability of clicks (possibly because of no relevance), return empty clicks,
            return np.array([])

        
        
        
        for i in range(min(count,observe_num+1)):                                  #from initiall, not generate clicks for bellow cut-off#
            doc_i = self.result[i].ranking
            clicks[doc_i] = np.random.binomial(n=1, p=click_prob[doc_i])  # generate the click
            assert i==doc_i


    
        if np.sum(clicks) <= 0:  # if no clicks generated, return empty
            return np.array([])

        self.setPropencityScores(clicks , eta)



        return clicks



input_file_name = sys.argv[1]           #99% of train data#
prediction= sys.argv[2]                 #prediction file that contains base ranker scores for 99% of train data#                                                
output_file_name_naive= sys.argv[3]     #output file that we write data that will be fed to naive-svm#                                                
output_file_name_propensity= sys.argv[4]#output file that we write data that will be fed to propensity-svm#
output_file_name_heckman= sys.argv[5]   #output file where we write data that will be fed to heckman#                                              
sampling_times= int(sys.argv[6])        #number of passes (5)#
observe_num = int(sys.argv[7])          #cut off (1-30)#
eta= float(sys.argv[8])                 #eta=position bias severity#



#read test data#
input_file_name_test = "../set1.test.binary.txt"

file_test = open(input_file_name_test, "r")     
D_test={}
for f1 in file_test:
    qid=f1[f1.find(":")+1:f1.find(" ",f1.find(":"))]
    attributes=""
    if f1[-1]== "\n":
        attributes=f1[f1.find(" ", f1.find(":"))+1:-1]
    else:
        attributes = f1[f1.find(" ", f1.find(":"))+1:]     
    trueR = float(f1[:f1.find(" ")])
    # print(trueR)
    if qid not in D_test:                    
        # D[qid]=[]
        D_test[qid] = searchResult()
    newSearchItem = searchItem (1, trueR, attributes)             
    D_test[qid].result.append(newSearchItem)










#read train data, and prediction file#
file_train = open(input_file_name, "r")     

file_prediction = open(prediction, "r")                                                                                    

    

D={}
for f1 in file_train:

    qid=f1[f1.find(":")+1:f1.find(" ",f1.find(":"))]
    attributes=""
    if f1[-1]== "\n":
        attributes=f1[f1.find(" ", f1.find(":"))+1:-1]
    else:
        attributes = f1[f1.find(" ", f1.find(":"))+1:]     


    
    f2 = file_prediction.readline()                                                           
    ranking=float(f2[:-1])  
    trueR = float(f1[:f1.find(" ")])
    if qid not in D:                    
        D[qid] = searchResult()
    
    newSearchItem = searchItem (ranking, trueR, attributes)             
    
    D[qid].result.append(newSearchItem)



#### Start Sampling #####
D_new={}
D_train=D

D={}

qids = list(D_train)                 
#print qids
for sampling in range(sampling_times):      # number of passes
    for r in range(len(qids)):
        #r = random.randint(0,len(qids)-1)    #choose a random number to sample#
        for i in range(1,len(qids)*100):      #assuming that irrespective of how many sampling we are doing, the lenghth of qid would not exceed 100 times its initial length#
            newQID = qids[r]+"_"+str(i)       
            if newQID not in D_new:               
                D_new[newQID] = deepcopy(D_train[qids[r]])
                break

#### END Sampling #####



D_train=D_new



#### START CLICK GENERATION #####


for k in D_train: # for each key, sort the corresponding value
    #print k
    #D[k].doPrint()
    D_train[k].sortByRank()                                   
    #print "sorted"
    #D[k].doPrint()

    clicks= D_train[k].gen_clicks(eta)
    #print clicks
    #print D[k].getRankOfClicked(clicks)
    #print D[k].clicked





#### END CLICK GENERATION #####





#### START Writing Output (this data will be reranked by Heckman, niave svm and propensity svm)#####



#write propensity svm#


train_out = open(output_file_name_propensity+".train", "w")
test_out = open(output_file_name_propensity+".test", "w")


counter=1
for k in D_train:
    for c in D_train[k].clicked:
       train_out.write("1 qid:"+str(counter)+" cost:"+str(D_train[k].clicked[c])+" "+D_train[k].result[c].attributes+"\n")  
       lastRanking = -1
       for i in range(len(D_train[k].result)):                      
           if i ==c:
               continue
           assert(D_train[k].result[i].ranking > lastRanking)
           lastRanking = D_train[k].result[i].ranking
           train_out.write("0 qid:" + str(counter) + " " + D_train[k].result[i].attributes+"\n")

       counter = counter+1



for k in D_test:
    for c in range(len(D_test[k].result)):
       if  D_test[k].result[c].true_rel == 0:
           continue
       test_out.write("1 qid:"+str(counter)+" cost:1 "+D_test[k].result[c].attributes+"\n")  
                      

       for i in range(len(D_test[k].result)):
           if i ==c:
               continue
           
           test_out.write("0 qid:" + str(counter) + " " + D_test[k].result[i].attributes+"\n")

       counter = counter+1







#write naive svm#

train_out = open(output_file_name_naive+".train", "w")
test_out = open(output_file_name_naive+".test", "w")


counter=1
for k in D_train:

    for c in D_train[k].clicked:  
       train_out.write("1 qid:" + str(counter) + " cost:1 " + D_train[k].result[c].attributes + "\n")                
       lastRanking = -1
       for i in range(len(D_train[k].result)):  
           if i ==c:
               continue
           assert(D_train[k].result[i].ranking > lastRanking)
           lastRanking = D_train[k].result[i].ranking
           train_out.write("0 qid:" + str(counter) + " " + D_train[k].result[i].attributes+"\n")

       counter = counter+1

for k in D_test:

    for c in range(len(D_test[k].result)):
       if  D_test[k].result[c].true_rel == 0:
           continue
       test_out.write("1 qid:"+str(counter)+" cost:1 "+D_test[k].result[c].attributes+"\n")  

       for i in range(len(D_test[k].result)):
           if i ==c:
               continue
 
           test_out.write("0 qid:" + str(counter) + " " + D_test[k].result[i].attributes+"\n")

       counter = counter+1








#write heckman#

train_out = open(output_file_name_heckman+".train", "w")
test_out = open(output_file_name_heckman+".test", "w")


toCreateNewQUD = True    #if want to creat a new qid for a new click, keep it true, if want to have multiple click in a query, keep it false#




if toCreateNewQUD:


  counter=1
  for k in D_train:

      for c in D_train[k].clicked:
          
         seen=-1
         if D_train[k].result[c].ranking <= observe_num:
             seen = 1      
         else:
             assert False
             seen = 0
         train_out.write(str(counter) + " 1 " + D_train[k].result[c].attributes + " " + str(D_train[k].result[c].ranking) + " " + str(seen) + "\n")                
         lastRanking = -1
         for i in range(len(D_train[k].result)):
             if i ==c:
                 continue
             assert(D_train[k].result[i].ranking > lastRanking)
             lastRanking = D_train[k].result[i].ranking
             if D_train[k].result[i].ranking <= observe_num:
                 seen = 1        
             else:
                 seen = 0
             train_out.write(str(counter) + " 0 " + D_train[k].result[i].attributes + " " + str(D_train[k].result[i].ranking) + " " + str(seen) + "\n")

         counter = counter+1






else:

  counter=1
  for k in D_train:

     for i in range(len(D_train[k].result)):
         if D_train[k].result[i].ranking <= observe_num:
             seen = 1
         else:
             seen = 0
         if i in D_train[k].clicked:
             train_out.write(str(counter) + " 1 " + D_train[k].result[i].attributes + " " + str(D_train[k].result[i].ranking) + " " + str(seen) + "\n")
         else:
             train_out.write(str(counter) + " 0 " + D_train[k].result[i].attributes + " " + str(D_train[k].result[i].ranking) + " " + str(seen) + "\n")

     counter = counter+1






for k in D_test:

    for c in range(len(D_test[k].result)):
       if  D_test[k].result[c].true_rel == 0:
           continue
       
       seen=1
       
       test_out.write(str(counter) + " 1 " + D_test[k].result[c].attributes + " " + str(D_test[k].result[c].ranking) + " " + str(seen) + "\n")                
       
       for i in range(len(D_test[k].result)):
           if i ==c:
               continue
           
           test_out.write(str(counter) + " 0 " + D_test[k].result[i].attributes + " " + str(D_test[k].result[i].ranking) + " " + str(seen) + "\n")

       counter = counter+1

#### End Writing Output #####
print "done\n"
