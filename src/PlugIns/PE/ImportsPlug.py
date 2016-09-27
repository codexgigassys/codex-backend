# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os, sys
source_path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
sys.path.insert(0,source_path)
from Sample import Sample

from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile

class ImportsPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.imports"

    def getName(self):
        return "imports"

    def getVersion(self):
        return 4

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        try:
            if (pelib.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']].VirtualAddress == 0):
                return ""
        except Exception, e:
            print str(e)
            return ""

        d=[]
        dir_ent_imp=None
        try:
            dir_ent_imp=pelib.DIRECTORY_ENTRY_IMPORT
        except Exception, e:
            print str(e)
            return ""
        for entry in dir_ent_imp:

            dll_name=(entry.dll).lower()
            l=[]
            for imp in entry.imports:
                if imp.name is not None:
                    l.append((imp.name).lower())
                else:
                    l.append("")
                #aux={}
                #aux["name"]=imp.name
                #aux["ordinal"]=imp.ordinal
                #l.append(aux)

            dic_ent={"lib":dll_name,"functions":l}
            d.append(dic_ent)

        return d

if __name__=="__main__":
    data=open(source_path+"/Test_files/test.exe","rb").read()
    sample=Sample()
    sample.setBinary(data)
    modules={}
    pfm=PEFileModule()
    modules[pfm.getName()]=pfm
    plug=ImportsPlug()
    plug.setModules(modules)
    plug.setSample(sample)
    res=plug.process()
    print(res)
