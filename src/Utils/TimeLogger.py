# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import time

class TimeLogger():
    def __init__(self):
        self.start_time=0
        self.log_dic={}
        
    def __delete__(self):
        pass
        
    
    def startCounter(self):
        self.start_time=time.time()
        
    def logTime(self,name):
        end=time.time()
        elapsed=(end-self.start_time)*1000
        self.log_dic[name]=elapsed
        self.start_time=time.time()
        
    def __str__(self):
        ret=""
        for l in self.log_dic:
            ret=ret+(str(l)+" -> "+str(self.log_dic[l]))+"\n"
        return ret

#****************TEST_CODE******************
def testCode():
    tl2=TimeLogger()
    tl=TimeLogger()
    tl.startCounter()
    a=0
    for i in range(0,1000):
        a+=1
    tl2.startCounter()
    tl.logTime("1000 loop")
    tl2.logTime("logTime")    
    a=0
    for i in range(0,10000):
        a+=1
    tl.logTime("10000 loop")
    
    a=0
    for i in range(0,100000):
        a+=1
    tl.logTime("100000 loop")
    
    print(str(tl))
    print("")
    print(str(tl2))
    
#****************TEST_EXECUTE******************
from test import test
test("-test_TimeLoger",testCode)
