# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
import hashlib
from pymongo import MongoClient
import gridfs
try:
    from secrets import env
except ImportError:
    from default_config import env

# Writes binaries on the DB
class PackageController():
    def __init__(self):
        client=MongoClient(env["files"]["host"],env["files"]["port"])
        db=client[env["db_files_name"]]
        self.fs=gridfs.GridFS(db)
        if(env["temporal_files_db"]):
            client_temp=MongoClient(env["temp_files"]["host"],env["temp_files"]["port"])
            db_temp=client_temp[env["db_temp_files_name"]]
            self.fs_temp=gridfs.GridFS(db_temp)

    def __delete__(self):
        pass

    # adds a file to the file database.
    def append(self,file_id,data,vt_blocked=False):
        if(env["temporal_files_db"]):
            self.fs_temp.put(data,filename=file_id,metadata={ "vt_blocked" :vt_blocked})
        else:
            self.fs.put(data,filename=file_id,metadata={ "vt_blocked" :vt_blocked})

    # returns searched file
    # returns None if it does not exist.
    def getFile(self,file_id):
        if( len(file_id) == 40):
            f=self.fs.find_one({"filename":file_id})
        elif(len(file_id) == 32):
            f=self.fs.find_one({"md5":file_id})
        else:
            print "PackageController: invalid file_id:"+str(file_id)+"(len="+str(len(file_id))+")"
            f=None
        if f==None:
            if env["temporal_files_db"]==False:
                return None
            else:
                if( len(file_id)==40):
                    f=self.fs_temp.find_one({"filename":file_id})
                elif(len(file_id) == 32):
                    f=self.fs_temp.find_one({"md5":file_id})
                else:
                    f=None
                    print "PackageController tmp: invalid file_id"+str(file_id)
                if f==None:
                    return None
        return f.read()


    def last_updated(self,number):
        if(env["temporal_files_db"]):
            client_fs = MongoClient(env["temp_files"]["host"],env["temp_files"]["port"])
        else:
            client_fs = MongoClient(env["files"]["host"],env["files"]["port"])
        db_files = client_fs[env["db_files_name"]]
        collection_files = db_files["fs.files"].find().sort([("_id", -1)]).limit(number)
        result=[]
        for document in collection_files:
            sha1=document.get('filename')
            md5=document.get('md5')
            tmp_doc={}
            tmp_doc["hash"] = {"sha1": sha1, "md5": md5}
            tmp_doc["upload_date"] = document.get('uploadDate') 
            result.append(tmp_doc)
        return result

    # returns None if the file can't be found on the DB.
    # 0 if the file exists.
    # 1 if the file exists but can't be downloaded.
    #### (Check if it is being used)
    def searchFile(self,file_id):
        ret=self.fs.find_one({"filename":file_id})
        if(ret==None):
            if(env["temporal_files_db"]==False):return None
            else:
                ret=self.fs_temp.find_one({"filename":file_id})
                if(ret==None):return None
        if(ret.metadata is not None and ret.metadata.get("vt_blocked")==True):
            return 1
        else: return 0

#****************TEST_CODE******************
def testCode():
    pc=PackageController(host="192.168.0.45",db_name="DATABASE_TEST")

    for dato in ["test_vt1","test_vt2"]:
        hs=hashlib.sha1(dato).hexdigest()
        res=pc.searchFile(hs)
        if(res==None):
            print("appending: "+dato)
            if(dato=="test_vt1"):
                pc.append(hs,dato,True)
            else:
                pc.append(hs,dato)
        if(res==0):
            print(dato+" already exists with:"+str(res))
        if(res==1):
            print(dato+" blocked:"+str(res))



    for dato in ["test_vt1","test_vt2","test_vt3"]:
        hs=hashlib.sha1(dato).hexdigest()
        res=pc.searchFile(hs)
        if(res==None):
            print("File does not exist: "+dato )
        if(res==0):
            print(dato+" File already exist:"+str(res))
        if(res==1):
            print(dato+" blocked:"+str(res))

#****************TEST_EXECUTE******************
#from Utils.test import test
#test("-test_PackageController",testCode)

if __name__ == "__main__":
    testCode()
