# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile
from Utils.InfoExtractor import *

class ResourceEntriesPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.res_entries"

    def getName(self):
        return "res_entries"

    def getVersion(self):
        return 6

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        ret = []
        if hasattr(pelib, 'DIRECTORY_ENTRY_RESOURCE'):
            i = 0
            for resource_type in pelib.DIRECTORY_ENTRY_RESOURCE.entries:
                if resource_type.name is not None:
                    name = "%s" % resource_type.name
                else:
                    name = "%s" % pefile.RESOURCE_TYPE.get(resource_type.struct.Id)
                if name == None:
                    name = "%d" % resource_type.struct.Id
                if hasattr(resource_type, 'directory'):
                    for resource_id in resource_type.directory.entries:
                        if hasattr(resource_id, 'directory'):
                            for resource_lang in resource_id.directory.entries:
                                try:
                                    data = pelib.get_data(resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size)
                                    #fd=open(name,'wb')
                                    #fd.write(data)
                                    #(data)
                                except:
                                    return "corrupt"
                                filetype = MIME_TYPE(data,False)
                                lang = pefile.LANG.get(resource_lang.data.lang, 'unknown')
                                sublang = pefile.get_sublang_name_for_lang( resource_lang.data.lang, resource_lang.data.sublang )
                                entry={}
                                entry["name"]=self._normalize(name)
                                entry["rva"]= self._normalize(hex(resource_lang.data.struct.OffsetToData))
                                entry["size"]=self._normalize(hex(resource_lang.data.struct.Size))
                                entry["type"]=self._normalize(filetype)
                                entry["lang"]=self._normalize(lang)
                                entry["sublang"]=self._normalize(sublang)
                                entry["sha1"]=SHA1(data)
                                ret.append(entry)

        return ret

