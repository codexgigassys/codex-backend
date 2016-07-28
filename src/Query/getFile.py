# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
import gridfs
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from secrets import env

#file_id="906f21f436b0dbb2c9cf37b80a90cdeb061ced3d"
#file_id="109bf9de7b82ffd7b8194aa3741b5d42ee878ebb"
file_id="6abec077e93226f4d9d9a5351092f3e0baef6d78"

client=MongoClient(env["files"]["host"],env["files"]["port"])
db=client[env["db_files_name"]]
fs=gridfs.GridFS(db)
f=fs.find_one({"filename":file_id})
if(f==None):
    print("No existe el archivo")
    exit(0)
data=f.read()
fd=open(file_id,"w+")
fd.write(data)
fd.close()
print("Archivo encontrado")
