from Utils.InfoExtractor import *

class Cataloger():
    def __init__(self,data=None):
        self.data=str(data)
        
    def __delete__(self):
        pass
    
    def catalogData(self):    
        mime=MIME_TYPE(self.data,True)
        return mime
    
    def catalog(self,data):    
        mime=MIME_TYPE(data,True)
        return mime    
        
        
#****************TEST_CODE******************
import os
def testCode():
    dir=os.getcwd()    
    #file=dir+"/Test_files/test.exe"
    file=dir+"/Test_files/t.lz"
    cat=Cataloger(open(file,'rb').read())
    res=cat.catalog()
    print(res)


#****************TEST_EXECUTE******************
from Utils.test import test
test("-test_Cataloger",testCode)
