# This file deletes a list of documents
# from the meta_container collection.
# ObjectId's to be deleted should be in ids.txt
# one id per line.
import pathmagic
from db_pool import *
from bson.objectid import ObjectId


def main():
    collection = db[envget('db_metadata_collection')]
    f = open("ids.txt", "r")
    for idd in f.readlines():
        clean_id = idd.replace('\n', '')
        print str(clean_id)
        collection.remove({"_id": ObjectId(clean_id)})


if __name__ == "__main__":
    main()
