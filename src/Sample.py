# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from Utils.TimeLogger import TimeLogger
from MetaDataPKG.Metadata import Metadata
from PackageControl.PackageController import *


class Sample:

    def __init__(self, packageController=None, metaController=None, versionController=None):
        self.sample_id = None

        self.pc = packageController
        self.mc = metaController
        self.vc = versionController
        # self.cataloger=cataloger

        self.binary = None
        self.binary_try_to_load = True

        self.metadata_storeada = Metadata()
        self.metadata_calculada = Metadata()
        self.metadata_try_to_load = True

        self.version_storeada = None
        self.version_calculada = {}
        self.version_try_to_load = True

        self.category = None

        # self.metaDB=None
        # self.metaCalc=None
        # self.metaDB_try=False

    def addAdditionalObject(self, obj):
        self.additional_objs.append(obj)

    def getAdditionalObjects(self):
        return self.additional_objs

    def setVersionController(self, versionController):
        self.vc = versionController

    def setPackageController(self, packageController):
        self.pc = packageController

    def setMetaController(self, metaController):
        self.mc = metaController

    # def setCataloger(self,cataloger):
    #    self.cataloger=cataloger

    def setStorageVersion(self, ver):
        self.version_storeada = ver

    def getCalculatedVersion(self):
        return self.version_calculada

    def getStorageVersion(self):
        if(self.version_storeada != None):
            return self.version_storeada
        if(self.version_try_to_load):
            self.version_try_to_load = False
            if(self.vc == None):
                return None
            self.version_storeada = self.vc.searchVersion(self.sample_id)
        return self.version_storeada

    def getCategory(self):
        if(self.category != None):
            return self.category
        st = self.getStorageVersion()
        if(st == None):
            return None
        self.category = st.get("category")
        return self.category

    # val=self.getStorageMetadata().get("mime_type")#cambiar
        # if(val!=None): return val
        # print("NOOOOOOOOOO")
        # return self.cataloger.catalog(self.getBinary())
        # remove from versions.

    def setCategory(self, cat):
        self.category = cat

    def getLastValue(self, key):
        val = self.metadata_calculada.getValue(key)
        if(val != None):
            return val
        if(self.metadata_try_to_load):
            self.metadata_try_to_load = False
            if(self.mc == None):
                return None
            self.metadata_storeada.setData(self.mc.read(self.sample_id))
        val = self.metadata_storeada.getValue(key)
        return val

    # if(self.metaCalc!=None):
        #    res=self.metaCalc.get(key)
        #    if(res!=None): return res
        #
        # if(self.metaDB!=None):
        #    return self.metaDB["particular_header"].get(key)
        #
        # if(self.metaDB_try):
        #    return None
        #
        # self.metaDB_try=True
        # if(self.mc==None):return None
        # self.metaDB=self.mc.read(self.sample_id)
        # if(self.metaDB==None):return None
        # return self.metaDB["particular_header"].get(key)

    def setStorageMetadata(self, meta):
        self.metadata_storeada = meta

    def getStorageMetadata(self):
        if(self.metadata_try_to_load):
            self.metadata_try_to_load = False
            if(self.mc == None):
                return None
            self.metadata_storeada.setData(self.mc.read(self.sample_id))
        return self.metadata_storeada

    def setCalculatedMetadata(self, cal):
        self.metadata_calculada = cal

    def getCalculatedMetadata(self):
        return self.metadata_calculada
    # if(self.metaDB!=None):
        #    return self.metaDB
        # if(self.metaDB_try):
        #    return None
        # self.metaDB_try=True
        # if(self.mc==None):return None
        # self.metaDB=self.mc.read(self.sample_id)
        # return self.metaDB

    def setCalculatedValue(self, path, value):
        self.metadata_calculada.setValue(path, value)

    def setID(self, sample_id):
        self.sample_id = sample_id

    def getID(self):
        return self.sample_id

    def setBinary(self, binary):
        self.binary = binary
        self.binary_try = True

    def getBinary(self):
        if(self.binary != None):
            return self.binary
        if(not self.binary_try_to_load):
            return None
        self.binary_try_to_load = False
        if(self.pc == None):
            # we use a temporary PackageController so we don't leave a mongo
            # cursor open.
            tmp_pc = PackageController()
            self.binary = tmp_pc.getFile(self.sample_id)
            return self.binary

        self.binary = self.pc.getFile(self.sample_id)
        return self.binary
