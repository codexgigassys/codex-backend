# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile
from Utils.InfoExtractor import *
import logging
import entropy

class SectionsPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.sections"

    def getName(self):
        return "sections"

    def getVersion(self):
        return 15

    def process(self):
        #print("SECTIONS")
        #logging.debug("loading pefile")
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        #logging.debug("iterating sections")
        ret=[]
        number=0

        for section in pelib.sections:
            #print(section)
            dic_sec={}
            dic_sec["name"]=repr(section.Name)

            dic_sec["size_raw_data"]=int(hex(section.SizeOfRawData),16)
            dic_sec["virtual_size"]=int(hex(section.Misc_VirtualSize ),16)
            dic_sec["characteristics"]=hex(section.Characteristics)

            if ( section.__dict__.get('IMAGE_SCN_MEM_WRITE', False)  and
                    section.__dict__.get('IMAGE_SCN_MEM_EXECUTE', False) ):
                dic_sec["write_executable"]="True"
            else:
                dic_sec["write_executable"]="False"

            data=section.get_data()
            #logging.debug("calculating hashes")
            dic_sec["sha1"]=SHA1(data)
            dic_sec["sha2"]=SHA256(data)
            dic_sec["md5"]=MD5(data)
            #logging.debug("calculating fuzzy")
            dic_sec["fuzzy_hash"]=getSsdeep(data)
            dic_sec["entropy"]=entropy.shannon_entropy(data) * 8
            #logging.debug("finished calculating")

            ret.append(dic_sec)

        return ret
