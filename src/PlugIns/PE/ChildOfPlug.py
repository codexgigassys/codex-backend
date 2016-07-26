from PlugIns.PlugIn import PlugIn

class ChildOfPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)
        
    def getPath(self):
        return "particular_header.child_of"
        
    def getName(self):
        return "child_of"
    
    def getVersion(self):
        return 1
            
    def process(self):
        return "Not_implemented"
