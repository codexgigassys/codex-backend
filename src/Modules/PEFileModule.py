# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from Modules.Module import Module
import traceback
import pefile
import logging


class PEFileModule(Module):

    def __init__(self):
        Module.__init__(self)

    def getName(self):
        return "pefileModule"

    def initialize(self, sample):
        if(self.already_initialized):
            return self.library
        self.already_initialized = True
        try:
            self.library = pefile.PE(data=sample.getBinary(), fast_load=True)
            # see if this initializations can be done on plugins.
            self.library.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])

        except pefile.PEFormatError:
            # print("parse fail")
            self.library = None
            # print(traceback.format_exc())
            logging.error("Error parsing pefileModule with sample:%s",
                          sample.getID(), exc_info=True)
