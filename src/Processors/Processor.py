# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from Utils.InfoExtractor import *
import datetime
import math
from Utils.TimeLogger import TimeLogger
import traceback
from PlugIns.Generic import *
import logging


class Processor():

    def __init__(self, sample):
        # self.result=Metadata() # result of processing
        self.sample = sample  # data for analyzing
        # self.sample.setCalculatedMetadata(self.result)
        self.version = sample.getStorageVersion()  # dictionary of current versions
        self.result_version = sample.getCalculatedVersion()  # up to date versions
        self.plugins = []  # plugins to execute.
        self.modules = {}  # Modules of libraries used by plugins.
        self.metadata_to_store = {}

    def __delete__(self):
        pass

    # General processing that gets executed for every sample.
    def process(self):
        self._addPlugIn(FuzzyPlug.FuzzyPlug())
        self._addPlugIn(HashPlug.HashPlug())
        self._addPlugIn(SizePlug.SizePlug())
        self._addPlugIn(DescPlug.DescPlug())
        self._addPlugIn(MimePlug.MimePlug())
        self._addPlugIn(DatePlug.DatePlug())

        return self.metadata_to_store

    def _executeAllPlugIns(self):
        for plug in self.plugins:
            plug.setSample(self.sample)
            plug.setModules(self.modules)
            self._executePlugIn(plug)

    def _addPlugIn(self, plug):
        self.plugins.append(plug)

    def _addModule(self, mod):
        self.modules[mod.getName()] = mod

    # Execute plugins in a safe way.
    def _executePlugIn(self, plugin):
        info_string = plugin.getName()
        code_version = plugin.getVersion()
        path = plugin.getPath()
        if(self._version_is_update(info_string, code_version)):
            return 0
        # compute
        try:
            logging.debug("Running %s v.%s PlugIn",
                          info_string, str(code_version))
            # tl=TimeLoger()
            # tl.startCounter()
            res = plugin.process()
            # tl.logTime(info_string)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            logging.error("Error in %s PlugIn with sample:%s",
                          info_string, self.sample.getID(), exc_info=True)
            res = "ERROR_EXECUTE_PLUGIN"
            logging.exception("**** Error File: %s ****" %
                              (self.sample.getID(),))
            logging.info("**** PlugIn    : %s ****" % (info_string,))
            err = str(traceback.format_exc())
            logging.info(err)
        self._update(plugin, res)
        return 0

    # check if the version of "info string" is up to date.
    def _version_is_update(self, info_string, code_version):
        if(self.version == None):
            return False
        ver = self.version.get(info_string)
        if(ver == None):
            return False
        if(ver < code_version):
            return False
        return True

    # saves the result and the version.
    def _update(self, plugin, res):
        code_version = plugin.getVersion()
        name = plugin.getName()
        info_string = plugin.getPath()
        self.sample.setCalculatedValue(info_string, res)
        # self.version[name]=code_version
        self.result_version[name] = code_version
        self.metadata_to_store[info_string] = res
        return 0

    # returns up to date versions.
    def getVersion(self):
        return self.result_version

    # redefine str()
    # def __str__(self):
    #    string=""
    #    for word in self.result:
    #        #tabs='\t'
    #        tabs="   "
    #        #for i in range(6-int((len(word)+1)/8)):
    #        #    tabs+="    "
    #        string+=(str(word)+":"+tabs+str(self.result[word])+'\n')
    #
    #    return string


#****************TEST_CODE******************
def testCode():
    pass

#****************TEST_EXECUTE******************
from Utils.test import test
test("-test_Processor", testCode)
