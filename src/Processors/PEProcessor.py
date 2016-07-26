from Processors.Processor import *
import traceback
import time
import string
#PlugIns
from PlugIns.PE import *
#Modulos
from Modules.PEFileModule import *
from Modules.MetaDataModule import *

class PEProcessor(Processor):

    def __init__(self,sample):
        Processor.__init__(self,sample)
                                
    def __delete__(self):
        Processor.__delete__(self)
    
    #metodo de procesamiento    
    def process(self):
        Processor.process(self)
        
        self._addModule(PEFileModule())
        self._addModule(MetaDataModule())
                
        self._addPlugIn(ImportsPlug.ImportsPlug())
        self._addPlugIn(EntropyPlug.EntropyPlug())
        self._addPlugIn(SectionsPlug.SectionsPlug())
        self._addPlugIn(ResourceEntriesPlug.ResourceEntriesPlug())
        self._addPlugIn(CheckEPSectionPlug.CheckEPSectionPlug())
        #self._addPlugIn(CRCCheckPlug.CRCCheckPlug())
        self._addPlugIn(TimeStampPlug.TimeStampPlug())
        self._addPlugIn(HeadersPlug.HeadersPlug())
        self._addPlugIn(VersionInfoPlug.VersionInfoPlug())
        self._addPlugIn(ChildOfPlug.ChildOfPlug())
        self._addPlugIn(CypherPlug.CypherPlug())
        self._addPlugIn(PackerVersionPlug.PackerVersionPlug())
        self._addPlugIn(AVAnalysisPlug.AVAnalysisPlug())
        self._addPlugIn(CheckPackerPlug.CheckPackerPlug())
        #self._addPlugIn(TestPlug.TestPlug())
        self._addPlugIn(AddImportsToTreePlug.AddImportsToTreePlug())
        self._addPlugIn(ExportsPlug.ExportsPlug())
        
        self._addPlugIn(CertficatePlug.CertficatePlug())
        
        self._addPlugIn(StringPlug.StringPlug())
        
            
        self._executeAllPlugIns()
        
        return self.metadata_to_store
            
#****************TEST_CODE******************
import time
from Sample import *

def testCode():
    file="Test_files/error_de_codificacion_en_nombre_de_libreria"
    data=open(file,"rb").read()
    
    start_time=time.time()
    dic={}
    sample=Sample()
    sample.setBinary(data)
    pe=PEProcessor(sample,dic)
    res=pe.process()
    print(res)
    #print(res["particular_header"]["sections"])
    elapsed=time.time()-start_time    
    print("Time Elapsed: "+str(elapsed*1000)+" ms")
    print("")
        
    
#****************TEST_EXECUTE******************
#from Utils.test import test
test("-test_PEProcessor",testCode)
