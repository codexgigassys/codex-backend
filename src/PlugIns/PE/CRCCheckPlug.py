# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile

class CRCCheckPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.crc"

    def getName(self):
        return "crc"

    def getVersion(self):
        return 2

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        crc_claimed = pelib.OPTIONAL_HEADER.CheckSum
        crc_actual  = pelib.generate_checksum()
        s={"claimed": crc_claimed, "actual": crc_actual}
        return s
