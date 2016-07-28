# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Utils.InfoExtractor import *

class HashPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)
        
    def getName(self):
        return "hash"
    
    def getVersion(self):
        return 1
            
    def process(self):
        data=self.sample.getBinary()
        dic={}
        dic["sha1"]=SHA1(data)
        dic["sha2"]=SHA256(data)
        dic["md5"]=MD5(data)
        return dic
