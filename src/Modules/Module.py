
class Module():
    def __init__(self,lib=None):
        self.library=lib
        if(lib==None):self.already_initialized=False
        else:self.already_initialized=True
        
    def getLibrary(self):
        return self.library
            
    def getName(self):
        pass
        
    def initialize(self,sample):
        pass
