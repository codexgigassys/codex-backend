# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
import ssdeep

def searchFuzzy(fuzz,limit,thresh):
    client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
    db=client[env["db_metadata_name"]]
    coll_meta=db["db_metadata_collection"]

    f1=coll_meta.find({},{"file_id":1,"fuzzy_hash":1}).limit(limit)
    l=[]
    for f in f1:
        l.append(f)

    ret={}
    for a in l:
        res=-1
        try:
            res=ssdeep.compare(a["fuzzy_hash"],fuzz)
        except:
            print(str(res)+"------"+str(a["fuzzy_hash"])+"-----"+str(a["file_id"]))
            continue
        if(res>=thresh):
            ret[a["file_id"]]=res
            
    return ret

def searchFull(search,limit):
    #print("1")
    client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
    #print("2")
    db=client[env["db_metadata_name"]]
    #print("3")
    coll_meta=db["db_metadata_collection"]
    #print("4")
    f1=coll_meta.find(search).limit(limit)
    #print("5")
    l=[]
    for f in f1:
        l.append(f)
    
    #print("6")
    ret=[]
    for a in l:
        ret.append(str(a["file_id"]))
    #print("7")
    
    return ret
    
