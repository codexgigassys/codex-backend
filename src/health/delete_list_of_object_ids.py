# This file deletes a list of documents
# from the meta_container collection.
# ObjectId's to be deleted should be in ids.txt
# one id per line.
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from db_pool import *
from bson.objectid import ObjectId

def main():
    collection = db[env["db_metadata_collection"]]
    f = open("ids.txt","r")
    for idd in f.readlines():
        clean_id = idd.replace('\n','')
        print str(clean_id)
        collection.remove({"_id": ObjectId(clean_id)})


if __name__ == "__main__":
        main()
