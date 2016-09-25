# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
from pymongo import MongoClient
from secrets import env

#Controlador versionando de los plugins ejecutados
class VersionController:
    def __init__(self):
        client=MongoClient(env["versions"]["host"],env["versions"]["port"])
        db=client[env["db_versions_name"]]
        self.collection=db.version_container
        #print(self.collection)

    def __delete__(self):
        pass

    def updateVersion(self,file_id,ver_dic):
        command={"$set":ver_dic}
        #print(command)
        self.collection.update_one({"file_id":file_id},command,upsert=True)

    def searchVersion(self,file_id):
        f=self.collection.find_one({"file_id":file_id})
        #print(f)
        return f


#****************TEST_CODE******************
def testCode():
    db=DBVersion()
    ver={}
    for i in range(0,10):
        ver[str(i)]=i+10
    #db.updateVersion("0000",ver)
    lver=db.loadVersion("0000")
    n=lver["3"]
    print(type(n))


#****************TEST_EXECUTE******************
from Utils.test import test
test("-test_VersionController",testCode)
