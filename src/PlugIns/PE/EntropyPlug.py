# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
import entropy


class EntropyPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.file_entropy"

    def getName(self):
        return "file_entropy"

    def getVersion(self):
        return 1

    def process(self):
        res = entropy.shannon_entropy(self.sample.getBinary()) * 8
        return res
