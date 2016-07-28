# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
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
