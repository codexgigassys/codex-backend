# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
import ssdeep



client=MongoClient(envget('metadata.host'),envget('metadata.port'))
db=client[envget('db_metadata_name')]
coll_meta=db[envget('db_metadata_collection')]

"""
f=coll_meta.count({"particular_header.packer_detection":"True"})
print("%s documentos encontrados"%(f,))

#for a in f:
#    print(a["file_id"])


f=coll_meta.count({"particular_header.packer_detection":"False"})
print("%s documentos falsos"%(f,))


f=coll_meta.count({"particular_header.packer_detection":"Unknown"})
print("%s documentos desconocidos"%(f,))
"""

f1=coll_meta.find({},{"file_id":1,"fuzzy_hash":1})
l=[]
for f in f1:
    l.append(f)

count=0
for a in l:
    count+=1
    for b in l[count:]:
        res=ssdeep.compare(a["fuzzy_hash"],b["fuzzy_hash"])
        if(res>0):
            print("%s - %s - %s"%(res,a["file_id"],b["file_id"]))

    print("***** %s ******"%(count,))

            #raw_input()

