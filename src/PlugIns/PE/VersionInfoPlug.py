# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os, sys
source_path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
sys.path.insert(0,source_path)

from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile
from Sample import Sample

class VersionInfoPlug(PlugIn):
    def __init_(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.version"

    def getName(self):
        return "version"

    def getVersion(self):
        return 3

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        res={}
        if(hasattr(pelib,"VS_VERSIONINFO")):
            vi={}
            vi["Length"]=pelib.VS_VERSIONINFO.Length
            vi["ValueLength"]=pelib.VS_VERSIONINFO.ValueLength
            vi["Type"]=pelib.VS_VERSIONINFO.Type
            res["version_info"]=vi

            if(hasattr(pelib,"VS_FIXEDFILEINFO")):
                ffi={}
                ffi["Signature"]=pelib.VS_FIXEDFILEINFO.Signature
                ffi["StrucVersion"]=pelib.VS_FIXEDFILEINFO.StrucVersion
                ffi["FileVersionMS"]=pelib.VS_FIXEDFILEINFO.FileVersionMS
                ffi["FileVersionLS"]=pelib.VS_FIXEDFILEINFO.FileVersionLS
                ffi["ProductVersionMS"]=pelib.VS_FIXEDFILEINFO.ProductVersionMS
                ffi["ProductVersionLS"]=pelib.VS_FIXEDFILEINFO.ProductVersionLS
                ffi["FileFlagsMask"]=pelib.VS_FIXEDFILEINFO.FileFlagsMask
                ffi["FileFlags"]=pelib.VS_FIXEDFILEINFO.FileFlags
                ffi["FileOS"]=pelib.VS_FIXEDFILEINFO.FileOS
                ffi["FileType"]=pelib.VS_FIXEDFILEINFO.FileType
                ffi["FileSubtype"]=pelib.VS_FIXEDFILEINFO.FileSubtype
                ffi["FileDateMS"]=pelib.VS_FIXEDFILEINFO.FileDateMS
                ffi["FileDateLS"]=pelib.VS_FIXEDFILEINFO.FileDateLS
                res["fixed_file_info"]=ffi

            if(hasattr(pelib,"FileInfo")):
                fst={}
                for entry in pelib.FileInfo:
                    if(hasattr(entry,"StringTable")):
                        for str_entry in entry.StringTable: # check this. its an array.
                            #print(str_entry.entries)
                            #print(dir(str_entry))
                            fst["LangID"]=str(str_entry.LangID)
                            fst["LegalCopyright"]=str(str_entry.entries.get("LegalCopyright"))
                            fst["InternalName"]=str(str_entry.entries.get("InternalName"))
                            fst["FileVersion"]=str(str_entry.entries.get("FileVersion"))
                            fst["CompanyName"]=str(str_entry.entries.get("CompanyName"))
                            fst["ProductName"]=str(str_entry.entries.get("ProductName"))
                            fst["ProductVersion"]=str(str_entry.entries.get("ProductVersion"))
                            fst["FileDescription"]=str(str_entry.entries.get("FileDescription"))
                            fst["OriginalFilename"]=str(str_entry.entries.get("OriginalFilename"))
                            fst["Comments"]=str(str_entry.entries.get("Comments"))
                            fst["LegalTrademarks"]=str(str_entry.entries.get("LegalTrademarks"))
                            fst["PrivateBuild"]=str(str_entry.entries.get("PrivateBuild"))
                            fst["SpecialBuild"]=str(str_entry.entries.get("SpecialBuild"))

                res["string_file_info"]=fst

        return res

if __name__=="__main__":
    data=open(source_path+"/Test_files/kernel32.dll","rb").read()
    sample=Sample()
    sample.setBinary(data)
    modules={}
    pfm=PEFileModule()
    modules[pfm.getName()]=pfm
    plug=VersionInfoPlug()
    plug.setModules(modules)
    plug.setSample(sample)
    res=plug.process()
    print(res)
