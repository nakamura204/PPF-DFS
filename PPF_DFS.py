import sys
import time
import resource
import math
import os
import psutil
import resource

path=sys.argv[1]
output=sys.argv[2]
minsup=float(sys.argv[3])
maxperiod=float(sys.argv[4])
minpr = float(sys.argv[5])

tidlist={}
hashing={}
first = 99999
last = 0
lno=0
def getPer_Sup(tids):
    #print(lno)
    global first, last, lno
    tids = list(set(tids))
    tids.sort()
    per=0
    sup=0
    cur=0
    if len(tids)==0:
        return 0
    if abs(first-tids[0])<= maxperiod:
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
    
def getPerSup(tids):
    #print(lno)
    global first, last,lno
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
    if abs(tids[len(tids)-1]-last) <=maxperiod:
        sup+=1
    if sup==0:
        return 0
    return sup

class Eclat_pfp():
    def __init__(self):
        self.mapSupport={}
        self.hashing={}
        self.itemsetCount=0
        self.writer=None
        self.minSup=0

    def findDelimiter(self, line):
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
    
    def scanDatabase(self,path):
        global lno,tidlist,maxperiod, minsup, first, last, minpr
        id1=0
        with open(path,'r') as f:
            for line in f:
                lno+=1
                #first=min(first,lno)
                #last=max(last,lno)
                line = line.strip()
                delimiter = self.findDelimiter([*line])
                s = [i.rstrip() for i in line.split(delimiter)]
                n=int(s[0])
                first = min(first, n)
                last = max(last, n)
                for i in range(1,len(s)):
                    si=s[i]
                    if abs(first-n)<=maxperiod:
                        if si not in self.mapSupport:
                            self.mapSupport[si]=[1,1,n]
                            tidlist[si]=[n]
                        else:
                            lp=abs(n-self.mapSupport[si][2])
                            if lp<=maxperiod:
                                self.mapSupport[si][0]+=1
                            self.mapSupport[si][1]+=1
                            self.mapSupport[si][2]=n
                            tidlist[si].append(n)
                    else:
                        if si not in self.mapSupport:
                            self.mapSupport[si]=[0,1,n]
                            tidlist[si]=[n]
                        else:
                            lp=abs(n-self.mapSupport[si][2])
                            if lp<=maxperiod:
                                self.mapSupport[si][0]+=1
                            self.mapSupport[si][1]+=1
                            self.mapSupport[si][2]=n
                            tidlist[si].append(n)
        for x,y in self.mapSupport.items():
            lp=abs(last-self.mapSupport[x][2])
            if lp<=maxperiod:
                self.mapSupport[x][0]+=1
        print(minsup,maxperiod, minpr)
        self.mapSupport={k: [v[1],v[0]] for k,v in self.mapSupport.items() if v[1]>=minsup and v[0]/(minsup+1)>=minpr}
        plist=[key for key,value in sorted(self.mapSupport.items(), key=lambda x:(x[1][0],x[0]),reverse=True)]
        return plist
    
    def save(self,prefix,suffix,tidsetx):
        global minsup,maxperiod,minpr
        tidsetx=list(set(tidsetx))
        if(prefix==None):
            prefix=suffix
        else:
            prefix=prefix+suffix
        val = getPerSup(tidsetx)
        val1= getPer_Sup(tidsetx)
        #print(prefix,tidsetx,val,val1)
        if len(tidsetx)>=minsup and val/(len(tidsetx)+1)>=minpr:
            self.itemsetCount+=1
            s1=str(prefix)+":"+str(len(tidsetx))+":"+str(val1)
            self.writer.write('%s \n'%s1)
    
    def Generation(self,prefix,itemsets,tidsets):
        global minpr,minsup
        if(len(itemsets)==1):
            i=itemsets[0]
            tidi=tidsets[0]
            self.save(prefix,[i],tidi)
            return
        for i in range(len(itemsets)):
            itemx=itemsets[i]
            if(itemx==None):
                continue
            tidsetx=tidsets[i]
            classItemsets=[]
            classtidsets=[]
            itemsetx=[itemx]
            for j in range(i+1,len(itemsets)):
                itemj=itemsets[j]
                tidsetj=tidsets[j]
                y=list(set(tidsetx) & set(tidsetj))
                val=getPerSup(y)
                #if(len(y)>=minsup and val/(len(y)+1)>=minpr):
                if len(y) >= minsup and val / (minsup+1) >= minpr:
                    classItemsets.append(itemj)
                    classtidsets.append(y)
            newprefix=list(set(itemsetx))+prefix
            self.Generation(newprefix, classItemsets,classtidsets)
            self.save(prefix,list(set(itemsetx)),tidsetx)
        
    def runAlgorithm(self,path,output,minsup,maxperiod,minpr):
        self.writer=open(output,'w')
        starttime=time.time()
        plist=self.scanDatabase(path)
        print(len(plist))
        for i in range(len(plist)):
            itemx=plist[i]
            tidsetx=tidlist[itemx]
            itemsetx=[itemx]
            itemsets=[]
            tidsets=[]
            for j in range(i+1,len(plist)):
                itemj=plist[j]
                tidsetj=tidlist[itemj]
                y1=list(set(tidsetx) & set(tidsetj))
                val=getPerSup(y1)
                #if(len(y1)>=minsup and val/(len(y1)+1)>=minpr):
                if len(y1) >= minsup and val/(minsup+1)>=minpr:
                    itemsets.append(itemj)
                    tidsets.append(y1)
            self.Generation(itemsetx,itemsets,tidsets)
            self.save(None,itemsetx,tidsetx)
        #print("eclat Total Itemsets:",self.itemsetCount)
        endtime=time.time()
        temp=(endtime-starttime)
        #print("eclat Time taken:",temp)
        #print("eclat Memory Space:",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        writer = open('resultEclat.csv', 'a')
        s = 'Patterns:' + str(self.itemsetCount) + '\n'
        writer.write(s)
        s = 'Time:' + str(temp) + '\n'
        writer.write(s)
        memory = resource.getrusage((resource.RUSAGE_SELF))
        s = 'Memory:' + str(memory.ru_maxrss) + '\n'
        writer.write(s)
        '''process = psutil.Process(os.getpid())
        memory = process.memory_full_info().uss  # process.memory_info().rss
        memory_in_MB = memory / (1024 * 1024)
        #return memory_in_MB
        print("Memory Space",memory_in_MB) '''          
                
                    
ch=Eclat_pfp()
ch.runAlgorithm(path,output,minsup,maxperiod,minpr)

