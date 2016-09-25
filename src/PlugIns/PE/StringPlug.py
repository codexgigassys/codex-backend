# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.MetaDataModule import *
from Modules.PEFileModule import PEFileModule
import validators
import re

class StringPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.strings"

    def getName(self):
        return "strings"

    def getVersion(self):
        return 3

    def process(self):
        ret={}
        data=""
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):data=self.sample.getBinary()
        else:
            for section in pelib.sections:
                data=data+section.get_data()

        regexp='[A-Za-z0-9/\-:.,_$&@=?%()[\]<> ]{4,}'
        strings=re.findall(regexp,data)
        aux={}
        for s in strings:
            aux[repr(s).lower()]=True

        unique_strings=[]
        for k in aux:
            unique_strings.append(k)

        mdc=self._getLibrary(MetaDataModule().getName())
        if(mdc==None):return ret


        searchUsed={}
        imports=self.sample.getLastValue("particular_header.imports")
        if(imports!=None ):
            for i in imports:
                searchUsed[i["lib"]]=True
                for f in i["functions"]:
                    searchUsed[f]=True

        exports=self.sample.getLastValue("particular_header.exports.symbols")
        if(exports!=None ):
            #print("No exports")
            for i in exports:
                searchUsed[i["name"]]=True
                if(hasattr(i,"forwarder_dll") and hasattr(i,"forwarder_function")):
                    searchUsed[i["forwarder_dll"]]=True
                    searchUsed[i["forwarder_function"]]=True

        version_p=self.sample.getLastValue("particular_header.version.string_file_info")
        if(version_p!=None ):
            for k in version_p.keys():
                searchUsed["'"+str(version_p[k])+"'"]=True



        raw=[]
        hidden=[]
        email=[]
        url=[]
        ip_l=[]

        dll=[]
        domain=[]
        interesting=[]

        registry=[]
        for s in unique_strings:
            # checking if the import is declared or not
            #print(s)
            #print(searchUsed.get(repr(s).lower()))
            #raw_input()
            if(searchUsed.get(s)==True): continue
            raw.append(s)

            # searching if its an import or not
            r=mdc.searchImportByName(s)
            if(r!=None):
                hidden.append(s)
                continue
            evaluado=eval(s)

            #searching dll
            r=mdc.searchDllByName(s)
            if(r!=None):
                dll.append(s)
                continue

            # searching for filenames
            types=["exe","dll","bat","sys","htm","html","js","jar","jpg",
                    "png","vb","scr","pif","chm","zip","rar","cab","pdf",
                    "doc","docx","ppt","pptx","xls","xlsx","swf","gif","pdb","cpp"]
            salir=False
            for pat in types:
                if(s.find("."+pat)!=-1):
                    interesting.append(s)
                    salir=True
                    break
            if salir: continue


            # searching email
            if(validators.email(evaluado)):
                email.append(s)
                continue

            # searching url
            if(validators.url(evaluado)):
                url.append(s)
                continue

            # searching ips
            if(validators.ipv4(evaluado)): #or validators.ipv6(evaluado)):
                ip_l.append(s)
                continue

            # searching registry
            if(s.find("HKLM\\")!=-1 or s.find("HKCU\\")!=-1 ):
                registry.append(s)
                continue

            # searching domains
            if(validators.domain(evaluado)):
                domain.append(s)
                continue

        ret["raw_strings"]=sorted(raw)
        if(len(hidden)>0):ret["hidden_imports"]=sorted(hidden)
        if(len(email)>0):ret["emails"]=sorted(email)
        if(len(url)>0):ret["urls"]=sorted(url)
        if(len(ip_l)>0):ret["ips"]=sorted(ip_l)
        if(len(dll)>0):ret["hidden_dll"]=sorted(dll)
        if(len(domain)>0):ret["domains"]=sorted(domain)
        if(len(interesting)>0):ret["interesting"]=sorted(interesting)
        if(len(registry)>0):ret["registry"]=sorted(registry)

        return ret
