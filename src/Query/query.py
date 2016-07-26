from pymongo import MongoClient
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from secrets import env

client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
db=client[env["db_metadata_name"]]
coll_meta=db[env["db_metadata_collection"]]

query={}
query["particular_header.file_entropy"]={"$gt":7.999}
res=coll_meta.find(query)
for e in res:
    print(("Encontrado: %s")%(e,))
