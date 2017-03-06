# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile


class CRCCheckPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.crc"

    def getName(self):
        return "crc"

    def getVersion(self):
        return 1

    def process(self):
        pelib = self._getLibrary(PEFileModule().getName())
        if(pelib is None):
            return ""

        crc_claimed = pelib.OPTIONAL_HEADER.CheckSum
        crc_actual = pelib.generate_checksum()
        s = "Claimed: 0x%x, Actual: 0x%x" % (crc_claimed, crc_actual)
        return self._normalize(s)
