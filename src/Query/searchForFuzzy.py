# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
import ssdeep

fuzzy_to_compare="12288:lTurEUKhROhnCzrwsrsNuRIHZB62atXtjBIuMAI0VpnJJyeVxy5la8AJv:lqrEJhROh8rwKsNrDK9xM3cJyeg0Jv"

client=MongoClient(envget('metadata.host'),envget('metadata.port'))
db=client[envget('db_metadata_name')]
coll_meta=db[envget('db_metadata_collection')]
print("loading")
f1=coll_meta.find({},{"file_id":1,"fuzzy_hash":1})
l=[]
for f in f1:
    l.append(f)
print("compearing")
count=0;reset=0
for a in l:
    try:
        res=ssdeep.compare(a["fuzzy_hash"],fuzzy_to_compare)
    except Exception, e:
        print str(e)
        continue
    if(res>=50):
        print("%s - %s"%(res,a["file_id"]))

    #print count
    #reset+=1; count+=1
    #if(reset>=1000):
    #    print(str(count)+" procesados")
    #    reset=0
