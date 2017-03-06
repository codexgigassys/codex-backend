# This checks that all the
# date attributes in av_analysis collection
# are valid datetime.datetime objects. If they are not
# the value sha1 and date of the offender is printed.
# It tries to fix the issue by using first_seen date.
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from db_pool import *
import datetime
from bson.objectid import ObjectId
from Utils.ProcessDate import process_date


def fix_date(r):
    str_date = r.get('date', r.get('first_seen'))
    if type(str_date) is not unicode:
        print("datenotunicode," + str(r.get('_id')) + "," +
                str(r.get('sha1')) + "," + str(r.get('date')) +
                "," + str(type(r.get('date'))))
        sys.stdout.flush()
        return False
    else:
        try:
            date = process_date(str_date)
        except Exception, e:
            print("failed to convert date for " +
                str(str_date) + " in " + str(r.get('_id')))
            sys.stdout.flush()
            return False

    collection = db["av_analysis"]
    collection.update_one({"_id": ObjectId(r.get('_id'))}, {
                          "$set": {"date": date}})
    return True


def main():
    collection = db["av_analysis"]
    start = 0
    count = 0
    test = 0
    mis = 0
    fixed = 0
    print_flag = 1000000
    res = collection.find(
        {}, {"date": 1, "sha1": 1, "first_seen": 1}, no_cursor_timeout=True).skip(start)
    for r in res:
        count += 1
        test += 1
        if (type(r.get('date')) is not datetime.datetime and r.get('date') is not None) or r.get('date') is None and r.get('first_seen') is not None:
            if(fix_date(r)):
                fixed += 1
            else:
                mis += 1
        if(test >= print_flag):
            test = 0
            print("count-fix-miss," + str(count) + "," + str(fixed) + "," + str(mis))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
