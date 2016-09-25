# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Utils.InfoExtractor import *

class MimePlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getName(self):
        return "mime_type"

    def getVersion(self):
        return 2

    def process(self):
        cat=MIME_TYPE(self.sample.getBinary(),True)
        self.sample.setCategory(cat)
        ver=self.sample.getCalculatedVersion()
        ver["category"]=cat
        return cat
