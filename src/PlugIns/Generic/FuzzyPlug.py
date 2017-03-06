# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Utils.InfoExtractor import *


class FuzzyPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getName(self):
        return "fuzzy_hash"

    def getVersion(self):
        return 1

    def process(self):
        return getSsdeep(self.sample.getBinary())
