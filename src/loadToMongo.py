# Tool to load malware into the mongo database.
import os
#path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','codex_library'))
import sys
import getopt
#sys.path.insert(0, path)
from PackageControl.PackageController import *
from Utils.Functions import recursive_read
import hashlib
import traceback
from Sample import *
from datetime import datetime
from Ram import *
#from IPython import embed
from Launcher import *

def thetime(start,finish,count):
    return str(count)+" loaded to mongo ( in "+str(int((finish-start).total_seconds()))+" seconds. ("+str(round(((finish-start).total_seconds()/3600),2))+" hours))"


def load_to_mongo2(folder_path):
    pc=PackageController()
    ram = Ram()
    files=recursive_read(folder_path)
    count=0
    reset=0
    already_loaded=0
    time_start = datetime.datetime.now()
    uploaded=0
    in_mem=0
    loaded_ram_counter=0
    lc=Launcher()
    while (uploaded < len(files)):
        loaded_ram_counter=0
        data_vector=[]
        print "loading files to memory"
        while (in_mem < len(files)):
            f=files[in_mem]
            file_cursor=open(f,"r")
            data_vector.append(file_cursor.read())
            in_mem=in_mem+1
            loaded_ram_counter=loaded_ram_counter+1
            if(loaded_ram_counter > 100):
                if(ram.free_percent() < 0.3):
                    print "Ram full"
                    break
        for data in data_vector:
            file_id=hashlib.sha1(data).hexdigest()
            print "loading to db: "+str(file_id)
            res=pc.searchFile(file_id)
            if(res==None):
                pc.append(file_id,data)
                sample=Sample()
                sample.setID(file_id)
                sample.setBinary(data)
                sample.setStorageVersion({}) 
                count+=1
                lc.launchAnalysisByID(sample)
            else:
                already_loaded+=1
            uploaded=uploaded+1

    result=str(already_loaded)+" were already loaded to mongo.\n"
    result+=thetime(time_start,datetime.datetime.now(),count)
    print result
    return result


