# This checks that all the
# file_id attributes in metadata documents
# are valid sha1 hashes. If they are not
# the value file_id and sha1 of the offender is printed.
import pathmagic
from db_pool import *


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True


def compare(_id, sha1, file_id):
    if sha1 != file_id or not is_sha1(sha1):
        print "idsha1fileid," + str(_id) + "," + str(sha1) + "," + str(file_id)
        sys.stdout.flush()
        return True
    else:
        return False


def main():
    collection = db[envget('db_metadata_collection')]
    start = 0
    count = 0
    test = 0
    mis = 0
    print_flag = 1000000
    res = collection.find({}, {"hash": 1, "file_id": 1},
                          no_cursor_timeout=True).skip(start)
    for r in res:
        count += 1
        test += 1
        if compare(r.get('_id'), r.get('hash', {}).get('sha1', ''), r.get('file_id')):
            mis += 1
        if(test >= print_flag):
            test = 0
            print "count-miss," + str(count) + "," + str(mis)
            sys.stdout.flush()


if __name__ == "__main__":
    main()
