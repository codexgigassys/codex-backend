# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile

class CheckEPSectionPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.ep"

    def getName(self):
        return "ep"

    def getVersion(self):
        return 1

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        name = ''
        ep = pelib.OPTIONAL_HEADER.AddressOfEntryPoint
        pos = 0
        for sec in pelib.sections:
            if (ep >= sec.VirtualAddress) and (ep < (sec.VirtualAddress + sec.Misc_VirtualSize)):
                name = sec.Name.replace('\x00', '')
                break
            else:
                pos += 1
        s = "%s %s %d/%d" % (hex(ep+pelib.OPTIONAL_HEADER.ImageBase), name, pos, len(pelib.sections))
        return self._normalize(s)
