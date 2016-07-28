# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from Processors.PEProcessor import *
from Processors.DummyProcessor import *

class ProcessorFactory():

    def __init__(self):
        pass
        
    def __delete__(self):
        pass

    def getHashProcessor(self,processor,sample):
        return HashProcessor(sample)
        
    def createProcessor(self,processor,sample):
        obj=None
        if(processor=="application/x-dosexec"):
            obj=PEProcessor(sample)
        else:
            obj=DummyProcessor(sample)
            
        return obj
    
#****************TEST_CODE******************
def testCode():
    pass

#****************TEST_EXECUTE******************
from Utils.test import test
test("-test_ProcessorFactory",testCode)

