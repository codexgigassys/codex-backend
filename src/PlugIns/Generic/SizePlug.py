# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn


class SizePlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getName(self):
        return "size"

    def getVersion(self):
        return 1

    def process(self):
        return len(self.sample.getBinary())
