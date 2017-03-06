# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from MetaControl.MetaController import MetaController
from Modules.Module import *


class MetaDataModule(Module):

    def __init__(self):
        Module.__init__(self)

    def getName(self):
        return "metaDataModule"

    def initialize(self, sample):
        if(not self.already_initialized):
            self.already_initialized = True
            self.library = MetaController()
        return self.library
