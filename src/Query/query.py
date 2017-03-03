# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from env import envget

client=MongoClient(envget('metadata.host'),envget('metadata.port'))
db=client[envget('db_metadata_name')]
coll_meta=db[envget('db_metadata_collection')]

query={}
query["particular_header.file_entropy"]={"$gt":7.999}
res=coll_meta.find(query)
for e in res:
    print(("Found: %s")%(e,))
