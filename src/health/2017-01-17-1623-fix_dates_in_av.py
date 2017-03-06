# AV analysis downloaded with vt public key have no first_seen
# We should use the last scan date to get an aproximation
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from db_pool import *

from MetaControl.MetaController import *


# Walk through a dictionary structure
def read_from_dictionary(source, dic):
    path = source.split('.')
    root = dic
    for p in path:
        try:
            root = root.get(p)
            if(root == None):
                return None
        except Exception, e:
            print str(e)
            return None
    return root


def main():
    mdc = MetaController()

    collection = db["av_analysis"]
    all_analysis = collection.find({"date": None})
    count = 0
    reset = 0
    for analysis in all_analysis:
        count += 1
        reset += 1
        if reset == 1000:
            reset = 0
            print("Count: %s" % count)
        file_id = analysis.get('sha1')
        date_stored = analysis.get('date')
        if(date_stored != None):
            # mdc.save_first_seen(file_id,date_stored) #Uncoment to copy all av
            # dates to meta dates
            continue

        # Trying to get the best date
        date_registers = ['first_seen',
                          'additional_info.first_seen_itw', 'scan_date']
        for register in date_registers:
            vt_date = read_from_dictionary(register, analysis)
            if vt_date != None:
                break

        try:
            # The "date" value is use to speed up time queries for av
            # signatures
            new_date = process_date(vt_date)
        except ValueError:
            new_date = None
            print "fix_dates_in_av: invalid date in AV_metda:" + str(vt_date)

        command = {"$set": {"date": new_date}}
        try:
            collection.update_one({"sha1": file_id}, command, upsert=False)
        except:
            print("**** Error File: %s ****" % (file_id,))
            print(command)
            err = str(traceback.format_exc())
            print(err)
            continue
        mdc.save_first_seen(file_id, new_date)
        print("%s fixed -> new date: %s" % (file_id, new_date))


if __name__ == "__main__":
    main()
