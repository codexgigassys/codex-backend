from PlugIns.PlugIn import PlugIn
from Utils.InfoExtractor import *

class DescPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)
        
    def getName(self):
        return "description"
    
    def getVersion(self):
        return 1
            
    def process(self):
        return MIME_TYPE(self.sample.getBinary(),False)    
