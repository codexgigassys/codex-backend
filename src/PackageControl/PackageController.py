# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
import hashlib
from pymongo import MongoClient
import gridfs
from secrets import env 

#Almacena los binarios dentro de la base de datos
class PackageController():

        def __init__(self):
            client=MongoClient(env["files"]["host"],env["files"]["port"])
            db=client[env["db_files_name"]]
            self.fs=gridfs.GridFS(db)
            
        def __delete__(self):
            pass
            
        #agrega la data de un archivo dentrol de un paquete appendeado
        def append(self,file_id,data,vt_blocked=False):
            self.fs.put(data,filename=file_id,metadata={ "vt_blocked" :vt_blocked})    
                
        #devuelve el archivo buscado
        #None si no existe    
        def getFile(self,file_id):
            f=self.fs.find_one({"filename":file_id})
            if f==None : return None
            return f.read()
            
        #devuelve la entrada del archivo del indice global
        #None si no existe
        # 0 if the file exists.
        # 1 if the file exists but can't be downloaded.
        ####Ver si no se usa y sacarla!
        def searchFile(self,file_id):
            ret=self.fs.find_one({"filename":file_id})
            if(ret==None):
                return None
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
            print("Appendeando: "+dato)
            if(dato=="test_vt1"):    
                pc.append(hs,dato,True)
            else:
                pc.append(hs,dato)
        if(res==0):
            print(dato+" ya existe con:"+str(res))
        if(res==1):
            print(dato+" bloqueado:"+str(res))
        
            
    
    for dato in ["test_vt1","test_vt2","test_vt3"]:
        hs=hashlib.sha1(dato).hexdigest()
        res=pc.searchFile(hs)
        if(res==None):
            print("No existe el archivo: "+dato )
        if(res==0):
            print(dato+" ya existe con:"+str(res))
        if(res==1):
            print(dato+" bloqueado:"+str(res))
    
#****************TEST_EXECUTE******************
#from Utils.test import test
#test("-test_PackageController",testCode)

if __name__ == "__main__":
    testCode()
