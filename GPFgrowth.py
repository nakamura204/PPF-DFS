'''import math
import sys
import time
import resource
path=sys.argv[1]
output=sys.argv[2]
minSup=float(sys.argv[3])
maxperiod=float(sys.argv[4])
minpr= float(sys.argv[5])
frequentitems=0
periodic={}
lno=0
rank={}
rankdup={}
class Node(object):
    def __init__(self, item, children):
        self.item = item
        self.children = children
        self.parent = None
        self.tids = []

    def addChild(self, node):
        self.children[node.item] = node
        node.parent = self
class Tree(object):
    def __init__(self):
        self.root = Node(None, {})
        self.summaries = {}
        self.info={}
    def add_transaction(self,transaction,tid):
        curr_node=self.root
        for i in range(len(transaction)):
            if transaction[i] not in curr_node.children:
                new_node=Node(transaction[i],{})
                curr_node.addChild(new_node)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(new_node)
                else:
                    self.summaries[transaction[i]]=[new_node]                    
                curr_node=new_node                
            else:
                        curr_node=curr_node.children[transaction[i]]            
            curr_node.tids=curr_node.tids+tid
    def get_condition_pattern(self,alpha):
        final_patterns=[]
        final_sets=[]
        for i in self.summaries[alpha]:
            q= self.genrate_tids(i)
            set1=i.tids 
            set2=[]
            while(i.parent.item!=None):
                set2.append(i.parent.item)
                i=i.parent
            if(len(set2)>0):
                set2.reverse()
                final_patterns.append(set2)
                final_sets.append(set1)
        final_patterns,final_sets,info=cond_trans(final_patterns,final_sets)
        return final_patterns,final_sets,info
    def genrate_tids(self,node):
        final_tids=node.tids
        return final_tids
    def remove_node(self,node_val):
        for i in self.summaries[node_val]:
            i.parent.tids = i.parent.tids + i.tids
            del i.parent.children[node_val]
            i=None
    def get_ts(self,alpha):
        temp_ids=[]
        for i in self.summaries[alpha]:
            temp_ids+=i.tids
        return temp_ids
                
    def generate_patterns(self,prefix):
        for i in sorted(self.summaries,key= lambda x:(self.info.get(x)[0],-x)):
            pattern=prefix[:]
            pattern.append(i)
            s=saveperiodic(pattern)
            g=self.get_ts(i)
            if getPer_Sup(g) >= minpr:
                #print(s,self.info.get(i))
                n=self.info.get(i)
                yield(pattern)
                patterns,tids,info=self.get_condition_pattern(i)
                conditional_tree=Tree()
                conditional_tree.info=info.copy()
                for pat in range(len(patterns)):
                    conditional_tree.add_transaction(patterns[pat],tids[pat])
                if(len(patterns)>0):
                    for q in conditional_tree.generate_patterns(pattern):
                        yield q
            self.remove_node(i)


def getPer_Sup(tids):
    tids=list(set(tids))
    tids.sort()
    cur=0
    per=0
    sup=0
    if len(tids)==0:
        return 0
    if abs(0-tids[0])<=maxperiod:
        sup+=1
    for i in range(len(tids)-1):
        j=i+1
        if abs(tids[j]-tids[i])<=maxperiod:
            sup+=1
    if abs(lno-tids[len(tids)-1])<=maxperiod:
        sup+=1
    return sup       

def cond_trans(cond_pat,cond_tids):
    pat=[]
    tids=[]
    data1={}
    for i in range(len(cond_pat)):
        for j in cond_pat[i]:
            if j in data1:
                data1[j]= data1[j] + cond_tids[i]
            else:
                data1[j]=cond_tids[i]
    up_dict={}
    for m,n in data1.items():
        up_dict[m]=[len(n),getPer_Sup(data1[m])]
    up_dict={k: v for k,v in up_dict.items() if v[0]>=minSup and v[1]>=minpr*(minSup+1)}
    count=0
    for p in cond_pat:
        p1=[v for v in p if v in up_dict]
        trans=sorted(p1, key= lambda x: (up_dict.get(x)[0],-x), reverse=True)
        if(len(trans)>0):
            pat.append(trans)
            tids.append(cond_tids[count])
        count+=1
    return pat,tids,up_dict
def update_transactions1(list_of_transactions,dict1,rank):
    list1=[]
    for tr in list_of_transactions:
        list2=[int(tr[0])]
        for i in range(1,len(tr)):
            if tr[i] in dict1:
                list2.append(rank[tr[i]])                       
        if(len(list2)>=2):
            basket=list2[1:]
            basket.sort()
            list2[1:]=basket[0:]
            list1.append(list2)
    return list1
def build_tree(data,info):
    root_node=Tree()
    root_node.info=info.copy()
    for i in range(len(data)):
        set1=[]
        set1.append(data[i][0])
        root_node.add_transaction(data[i][1:],set1)
    return root_node
def generate_dict(transactions):
    global rank
    data={}
    for tr in transactions:
        for i in range(len(tr)):
            if tr[i] not in data:
                data[tr[i]]=[0,int(tr[0]),1]
            else:
                lp=int(tr[0])-data[tr[i]][1]
                if lp<=maxperiod:
                    data[tr[i]][0]+=1
                data[tr[i]][1]=int(tr[0])
                data[tr[i]][2]+=1
    data={k: [v[2],v[0]] for k,v in data.items() if v[0]>=minSup and v[0]>= minpr*(minSup+1)}
    genList=[k for k,v in sorted(data.items(),key=lambda x: (x[1][0],x[0]),reverse=True)]
    rank = dict([(index,item) for (item,index) in enumerate(genList)])
    return data,genList
def saveperiodic(itemset):
    t1=[]
    for i in itemset:
        t1.append(rankdup[i])
    return t1
#global pfList,lno,rank2,rankdup,minsup,maxperiod
def main():
    global pfList,lno,rank2,rankdup,minSup,maxperiod
    with open(path,'r') as f:
        list_of_transactions=[]
        for line in f:    
            li=line.split() 
            list_of_transactions.append(li)
            lno+=1
    f.close()
    #minSup=int(math.ceil(minSup*lno)/100)
    #maxperiod=int(math.ceil(maxperiod*lno)/100)
    print(minSup,maxperiod)
    generated_dict,pfList=generate_dict(list_of_transactions)  
    updated_transactions1=update_transactions1(list_of_transactions,generated_dict,rank)
    for x,y in rank.items():
            rankdup[y]=x
    info={rank[k]: v for k,v in generated_dict.items()}
    list_of_transactions=[]
    Tree1= build_tree(updated_transactions1,info)
    intpat=Tree1.generate_patterns([])
    return intpat
if(__name__ == "__main__"):
    starttime=int(round(time.time()*1000)) 
    frequentitems=0
    k=main()
    with open(output, 'w') as f:
        for x in k:
            st=saveperiodic(x)
            f.write('%s \n'%st)
    with open(output,'r') as fi:
        for line in fi:
            frequentitems+=1
    endtime=int(round(time.time()*1000))
    temp=endtime-starttime
    #print("conditionalNodes count:",conditionalnodes)
    print("partial periodic frequent",frequentitems)
    print("Time Taken:",temp)
    print("Memory Space",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)  '''  




import math
import sys
import time
import resource
path=sys.argv[1]
output=sys.argv[2]
minSup=float(sys.argv[3])
maxperiod=float(sys.argv[4])
minpr=float(sys.argv[5])
frequentitems=0
periodic={}
lno=0
rank={}
rankdup={}
first = 9999999
last = 0
class Node(object):
    def __init__(self, item, children):
        self.item = item
        self.children = children
        self.parent = None
        self.tids = []

    def addChild(self, node):
        self.children[node.item] = node
        node.parent = self
class Tree(object):
    def __init__(self):
        self.root = Node(None, {})
        self.summaries = {}
        self.info={}
    def add_transaction(self,transaction,tid):
        curr_node=self.root
        for i in range(len(transaction)):
            if transaction[i] not in curr_node.children:
                new_node=Node(transaction[i],{})
                curr_node.addChild(new_node)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(new_node)
                else:
                    self.summaries[transaction[i]]=[new_node]                    
                curr_node=new_node                
            else:
                        curr_node=curr_node.children[transaction[i]]            
            curr_node.tids=curr_node.tids+tid
    def get_condition_pattern(self,alpha):
        final_patterns=[]
        final_sets=[]
        for i in self.summaries[alpha]:
            q= self.genrate_tids(i)
            set1=i.tids 
            set2=[]
            while(i.parent.item!=None):
                set2.append(i.parent.item)
                i=i.parent
            if(len(set2)>0):
                set2.reverse()
                final_patterns.append(set2)
                final_sets.append(set1)
        final_patterns,final_sets,info=cond_trans(final_patterns,final_sets)
        return final_patterns,final_sets,info
    def genrate_tids(self,node):
        final_tids=node.tids
        return final_tids
    def remove_node(self,node_val):
        for i in self.summaries[node_val]:
            i.parent.tids = i.parent.tids + i.tids
            del i.parent.children[node_val]
            i=None
    def get_ts(self,alpha):
        temp_ids=[]
        for i in self.summaries[alpha]:
            temp_ids+=i.tids
        return temp_ids
                
    def generate_patterns(self,prefix):
        global minSup,minpr
        for i in sorted(self.summaries,key= lambda x:(self.info.get(x)[0],-x)):
            pattern=prefix[:]
            pattern.append(i)
            g=self.get_ts(i)
            g=list(set(g))
            s=saveperiodic(pattern)
            n=self.info.get(i)
            #if len(g)>=minSup and getPer_Sup(g)/(len(g)+1)>=minpr:
            if len(g)>=minSup and getPeriodicRatio(g) >= minpr:
            #if len(g) >= minSup and getPer_Sup(g) / (minSup + 1) >= minpr:
                yield(pattern)
                patterns,tids,info=self.get_condition_pattern(i)
                conditional_tree=Tree()
                conditional_tree.info=info.copy()
                for pat in range(len(patterns)):
                    conditional_tree.add_transaction(patterns[pat],tids[pat])
                if(len(patterns)>0):
                    for q in conditional_tree.generate_patterns(pattern):
                        yield q
            self.remove_node(i)


def getPer_Sup(tids):
    global first, last, lno
    tids=list(set(tids))
    tids.sort()
    cur=0
    per=0
    sup=0
    if abs(first-tids[0])<=maxperiod:
        sup+=1
    for i in range(len(tids)-1):
        j=i+1
        if abs(tids[j]-tids[i])<=maxperiod:
            sup+=1
    if abs(last-tids[len(tids)-1])<=maxperiod:
       sup+=1
    return sup    

def getPeriodicRatio(tids):
    global first, last, lno
    tids=list(set(tids))
    tids.sort()
    per=0
    sup=0
    cur=0
    if len(tids)==0:
        return 0
    if abs(first-tids[0]) <= maxperiod:
        sup+=1
    for j in range(len(tids)-1):
        i=j+1
        per=abs(tids[i]-tids[j])
        if(per<=maxperiod):
            sup+=1
        cur=tids[j]
    if abs(last-tids[len(tids)-1])<=maxperiod:
        sup+=1
    if sup==0:
        return 0
    return sup/(len(tids)+1)

def cond_trans(cond_pat,cond_tids):
    global minSup,minpr
    pat=[]
    tids=[]
    data1={}
    for i in range(len(cond_pat)):
        for j in cond_pat[i]:
            if j in data1:
                data1[j]= data1[j] + cond_tids[i]
            else:
                data1[j]=cond_tids[i]
    up_dict={}
    for m,n in data1.items():
        up_dict[m]=[list(set(n)),getPer_Sup(data1[m])]
    up_dict={k: v for k,v in up_dict.items() if len(v[0])>=minSup and v[1] >=minpr*(minSup+1)}
    count=0
    for p in cond_pat:
        p1=[v for v in p if v in up_dict]
        trans=sorted(p1, key= lambda x: (up_dict.get(x)[0],-x), reverse=True)
        if(len(trans)>0):
            pat.append(trans)
            tids.append(cond_tids[count])
        count+=1
    return pat,tids,up_dict
def update_transactions1(list_of_transactions,dict1,rank):
    list1=[]
    for tr in list_of_transactions:
        list2=[int(tr[0])]
        for i in range(1,len(tr)):
            if tr[i] in dict1:
                list2.append(rank[tr[i]])                       
        if(len(list2)>=2):
            basket=list2[1:]
            basket.sort()
            list2[1:]=basket[0:]
            list1.append(list2)
    return list1
def build_tree(data,info):
    root_node=Tree()
    root_node.info=info.copy()
    for i in range(len(data)):
        set1=[]
        set1.append(data[i][0])
        root_node.add_transaction(data[i][1:],set1)
    return root_node
def generate_dict(transactions):
    global rank,maxperiod, lno, first, last
    data={}
    k=0
    for tr in transactions:
        k+=1
        n = int(tr[0])
        first = min(first, n)
        last = max(last, n)
        for i in range(1,len(tr)):
            if abs(first-n)<=maxperiod:
                if tr[i] not in data:
                    data[tr[i]]=[1,n,1]
                else:
                    lp=int(tr[0])-data[tr[i]][1]
                    if lp<=maxperiod:
                        data[tr[i]][0]+=1
                    data[tr[i]][1]=int(tr[0])
                    data[tr[i]][2]+=1
            else:
                if tr[i] not in data:
                   data[tr[i]]=[0,n,1]
                else:
                   lp=int(tr[0])-data[tr[i]][1]
                   if lp<=maxperiod:
                       data[tr[i]][0]+=1
                   data[tr[i]][1]=int(tr[0])
                   data[tr[i]][2]+=1
    for x,y in data.items():
        if abs(last-data[x][1])<=maxperiod:
            data[x][0]+=1
    data={k: [v[2],v[0]] for k,v in data.items() if v[2]>=minSup and v[0]>=minpr*(minSup+1)}
    genList=[k for k,v in sorted(data.items(),key=lambda x: (x[1][0],x[0]),reverse=True)]
    #print(len(genList))
    rank = dict([(index,item) for (item,index) in enumerate(genList)])
    return data,genList
def saveperiodic(itemset):
    t1=[]
    for i in itemset:
        t1.append(rankdup[i])
    return t1
#global pfList,lno,rank2,rankdup,minsup,maxperiod

def findDelimiter(line):
    """Identifying the delimiter of the input file
    :param line: list of special characters may be used by a user to split the items in a input file
        :type line: list of string
        :returns: Delimited string used in the input file to split each item
        :rtype: string
        """
    l = [',', '*', '&', ' ', '%', '$', '#', '@', '!', '    ', '*', '(', ')']
    j = None
    for i in l:
        if i in line:
            return i
    return j

def main():
    global pfList,lno,rank2,rankdup,minSup,maxperiod
    with open(path,'r') as f:
        list_of_transactions=[]
        for line in f:
            line = line.strip()
            delimiter = findDelimiter([*line])
            li = [i.rstrip() for i in line.split(delimiter)]
            #li=line.split()
            list_of_transactions.append(li)
            lno+=1
    f.close()
    print(minSup,maxperiod,minpr)
    generated_dict,pfList=generate_dict(list_of_transactions)  
    updated_transactions1=update_transactions1(list_of_transactions,generated_dict,rank)
    for x,y in rank.items():
            rankdup[y]=x
    info={rank[k]: v for k,v in generated_dict.items()}
    list_of_transactions=[]
    Tree1= build_tree(updated_transactions1,info)
    intpat=Tree1.generate_patterns([])
    return intpat
if(__name__ == "__main__"):
    starttime=time.time()
    frequentitems=0
    k=main()
    with open(output, 'w') as f:
        for x in k:
            st=saveperiodic(x)
            f.write('%s \n'%st)
    with open(output,'r') as fi:
        for line in fi:
            frequentitems+=1
    endtime=time.time()
    temp=(endtime-starttime)
    #print("conditionalNodes count:",conditionalnodes)
    #print("partial periodic frequent:",frequentitems)
    #print("Time Taken:",temp)
    #print("Memory Space:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    writer = open('resultPFPgrowth.csv', 'a')
    s = 'Patterns:' + str(frequentitems) + '\n'
    writer.write(s)
    s = 'Time:' + str(temp) + '\n'
    writer.write(s)
    memory = resource.getrusage((resource.RUSAGE_SELF))
    s = 'Memory:' + str(memory.ru_maxrss) + '\n'
    writer.write(s)
