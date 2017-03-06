# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile


class TimeStampPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.date"

    def getName(self):
        return "date"

    def getVersion(self):
        return 1

    def process(self):
        pelib = self._getLibrary(PEFileModule().getName())
        if(pelib is None):
            return ""

        val = pelib.FILE_HEADER.TimeDateStamp
        ts = '0x%-8X' % (val)
        try:
            ts += ' [%s UTC]' % time.asctime(time.gmtime(val))
        except Exception, e:
            ts += ' [SUSPICIOUS]'

        return self._normalize(ts)
