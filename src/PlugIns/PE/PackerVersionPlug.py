# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn


class PackerVersionPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.packer_version"

    def getName(self):
        return "packer_version"

    def getVersion(self):
        return 1

    def process(self):
        return "Not_implemented"
