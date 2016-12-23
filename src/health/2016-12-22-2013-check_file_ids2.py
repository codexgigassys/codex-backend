# This checks that all the 
# file_id attributes in version_container documents
# are valid sha1 hashes. If they are not
# the value of _id, and file_id of the offender is printed.
# and the document gets deleted.
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from db_pool import *
from bson.objectid import ObjectId


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

def compare(_id,sha1,file_id):
    if sha1 != file_id or not is_sha1(sha1):
        print "idsha1fileid,"+str(_id)+","+str(sha1)+","+str(file_id)
        return True
    else:
        return False


def main():
    collection = db_ver["version_container"]
    start = 0
    count = 0
    test = 0
    mis = 0
    print_flag = 1000000
    res = collection.find({},{"_id": 1,"file_id": 1},no_cursor_timeout=True).skip(start)
    for r in res:
        count += 1
        test += 1
        doc_id = r.get("_id")
        file_id = r.get('file_id')
        if not is_sha1(file_id):
            mis +=1
            print str(doc_id)+","+str(file_id)
            collection.remove({"_id": ObjectId(str(doc_id))})
        if(test >= print_flag):
            test = 0
            print "count-miss,"+str(count)+","+str(mis)
    print "count-miss,"+str(count)+","+str(mis)


if __name__ == "__main__":
    main()
