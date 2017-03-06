# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn


class AVAnalysisPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.av_analysis"

    def getName(self):
        return "av_analysis"

    def getVersion(self):
        return 1

    def process(self):
        return "Not_implemented"
