# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.MetaDataModule import *


class AddImportsToTreePlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.imports_tree"

    def getName(self):
        return "imports_tree"

    def getVersion(self):
        return 1

    def process(self):
        imports = self.sample.getLastValue("particular_header.imports")
        if(imports is None):
            return "no_imports"
        if(len(imports) == 0):
            return "no_imports"
        mdc = self._getLibrary(MetaDataModule().getName())
        if(mdc is None):
            return "not_added"
        if(mdc.writeImportsTree(imports) == 0):
            return "added"
        else:
            return "not_added"
