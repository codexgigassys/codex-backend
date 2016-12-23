# This scripts iterates through meta_container 
# documents and searchs for a hash that do not 
# have a version_container document. Once found, it
# process it.
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from db_pool import *
from Utils.Functions import process_file
from IPython import embed

def check_if_has_version(file_id,collection_version):
    res = collection_version.find({"file_id": file_id}).limit(1)
    return res.count() != 0


def main():
    collection_version = db["version_container"]
    collection_meta = db[env["db_metadata_collection"]]
    start = 0
    count = 0
    test = 0
    mis = 0
    print_flag = 1000000
    res = collection_meta.find({},{"file_id": 1},no_cursor_timeout=True).skip(start)
    for r in res:
        count += 1
        test += 1
        file_id = r.get('file_id')
        if not check_if_has_version(file_id,collection_version):
            mis +=1
            process_file(file_id)
        if(test >= print_flag):
            test = 0
            print "count-miss,"+str(count)+","+str(mis)
    print "count-miss,"+str(count)+","+str(mis)

if __name__ == "__main__":
    main()
