from PlugIns.PlugIn import PlugIn

class SizePlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)
        
    def getName(self):
        return "size"
    
    def getVersion(self):
        return 1
            
    def process(self):
        return len(self.sample.getBinary())
