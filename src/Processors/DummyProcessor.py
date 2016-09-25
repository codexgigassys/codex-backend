# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from Processors.Processor import *
import traceback


class DummyProcessor(Processor):

        def __init__(self,sample):
            Processor.__init__(self,sample)

        def __delete__(self):
            Processor.__delete__(self)

        #metodo de procesamiento
        def process(self):
            Processor.process(self)
            #los plugins van aca
            self._executeAllPlugIns()
            return self.metadata_to_store



#****************TEST_CODE******************
import time

def testCode():
    file="Test_files/test.exe"
    data=open(file,"rb").read()

    start_time=time.time()
    dic={}
    dp=DummyProcessor(data,dic)
    print(dp.process())
    print(str(dic))
    elapsed=time.time()-start_time

    print("Time Elapsed: "+str(elapsed*1000)+" ms")
    print("")


#****************TEST_EXECUTE******************
#from Utils.test import test
test("-test_PEProcessor",testCode)
