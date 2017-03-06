# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
#import entropy


class TestPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.test"

    def getName(self):
        return "test"

    def getVersion(self):
        return 7

    def process(self):
        return "dist"
