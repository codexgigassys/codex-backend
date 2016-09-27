# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
from db_pool import *
#from IPython import embed
import re
from datetime import datetime as dtdatetime
import subprocess
from PackageControl.PackageController import *
from Sample import *
from Launcher import *
import csv
import json
import string

def is_iterable(s):
    try:
        iter(s)
    except:
        return False
    return True

def is_printable(str_value):
    for i in str_value:
        if i not in string.printable:
            return False
    return True

def str_to_hex(str_value):
    if str_value is not None:
        return " ".join("{:02x}".format(ord(c)).upper() for c in str_value)
    else:
        return ""

def replace_non_printable_with_dot(str_value):
    str_list=list(str_value)
    for index,char in enumerate(str_list):
        if(not is_printable(char)):
            str_list[index]=u"."
    return "".join(str_list)

def display_with_hex(str_value):
    if str_value is not None:
        cleaned_str = replace_non_printable_with_dot(str_value)
        return str(str_to_hex(str_value))+" ["+str(cleaned_str)+"]"
    else:
        return ""

def clean_tree(s):
    if type(s)==dict:
        for child in s.keys():
            s[child] = clean_tree(s[child])
    elif type(s)==list:
        for index,value in enumerate(s):
            s[index]=clean_tree(value)
    elif type(s)==str or type(s)==unicode:
        if(not is_printable(s)):
            return display_with_hex(s)
        else:
            return s
    elif isinstance(s,(int,long,float)):
        return s
    elif s is None:
        return s
    else:
        print str(type(s))
        if(is_iterable(s) and not is_printable(s)):
            return display_with_hex(s)
        else:
            return str(s)
    print str(s)
        #embed()
    return s
 

def to_bool(string):
    string=string.strip().lower()
    if string=="false" or string is None:
        return False
    else:
        return bool(string)


def jsonize(data):
    return json.dumps(data, sort_keys=False, indent=4)

# Given a date in str (epoch or ISO)
# will return a datetime object.
def process_date(str_date):
    if str_date is None:
        return None
    str_date=str_date.strip()
    if str_date=="":
        return None
    if str_date.isdigit():
        return dtdatetime.fromtimestamp(int(str_date))
    else:
        return dtdatetime.strptime(str_date,"%Y-%m-%d %H:%M:%S")

# Checks if the meta has a date. If it doesn't
# it updates it. If a date is found, the oldest
# date will get saved.
def update_date(file_id,date):
    if file_id is None or date is None:
        return
    mdc=MetaController()
    res=mdc.read(file_id)
    if res is not None:
        if res.get('date') is not None:
            if(res["date"] > date):
                mdc.write(file_id,{"date": date})
                return
        else:
            mdc.write(file_id,{"date": date})


def log_event(event,file_hash,comments=""):
    with open("logs.csv","a+") as logfile:
        csv_writer=csv.writer(logfile)
        csv_writer.writerow([str(dtdatetime.now().isoformat()),str(event),str(file_hash),str(comments)])


def change_date_to_str(res):
    if res is None:
        return None
    for date_key in ["date","upload_date"]:
        if res.get(date_key) is None:
            pass
        else:
            res[date_key]=str(res.get(date_key))
    return res


def process_file(file_hash):
    if file_hash is None:
        return None
    print "process_file("+str(file_hash)+")"
    pc=PackageController()
    res=pc.getFile(file_hash)
    if res==None:return None
    sam_id=file_hash
    sample=Sample()
    sample.setID(sam_id)
    sample.setBinary(res)
    sample.setStorageVersion({})
    lc=Launcher()
    lc.launchAnalysisByID(sample)
    log_event("process",str(file_hash))
    return 0


def execute(comand):
    process=os.popen(comand)
    preprocessed = process.read()
    process.close()
    #print(preprocessed)
    return preprocessed

def recursive_read(object):
    files=[]
    if os.path.isdir(object):
        for root, dirs, filenames in os.walk(object):
            for name in filenames:
                files.append(os.path.join(root, name))
    elif os.path.isfile(object):
        files.append(object)
    else:
        print "You must supply a file or directory!"
        return None
    return files

def call_with_output(array):
    p = subprocess.Popen(array, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err = p.communicate()
    return output

#strip and change to lowercase
def clean_hash(hash):
    if hash is None or hash == "":
        return None
    else:
        hash = hash.strip().lower()
        m = re.search('[a-f0-9]+',hash)
        return m.group(0)



def save_file_from_vt(hash_id):
    downloaded_file=download_from_virus_total(hash_id)
    if(downloaded_file==None):
        return None

    data_bin=downloaded_file
    file_id=hashlib.sha1(data_bin).hexdigest()
   # print "file_id="+str(file_id)
    pc=PackageController()
    res=pc.searchFile(file_id)
    if(res==None): # File not found. Add it to the package.
        pc.append(file_id,data_bin,True)
        print("Added: %s" % (file_id,))
    return file_id


#returns true if a hash is md5 or sha1 valid. False otherwise
def valid_hash(hash):
    return (len(hash)==32 or len(hash)==40) and re.search('^[a-f0-9]+$',hash) is not None


# clean hashes and search in the meta collection.
# returns file_id if it was found. None if it was not.
def get_file_id(hash):
    hash=clean_hash(hash)
    if not valid_hash(hash):
        return None
    if len(hash)==32:
        ret = search_by_hash_and_type(hash,"md5")
    elif len(hash)==40:
        ret = search_by_hash_and_type(hash,"sha1")
    if ret is not None and ret[0] is not None:
        return ret[0].get('sha1')
    else:
        return None

# Given a hash and a type (md5 or file_id (sha1))
# it will search in meta collection.
def search_by_hash_and_type(hash,type):
    if type is not "md5" and type is not "sha1":
        return None
    search={'$and': [{'hash.'+type: hash}]}
    retrieve={'file_id': 1}
    coll_meta=db.meta_container
    f1=coll_meta.find(search,retrieve)
    ret=cursor_to_dict(f1,retrieve)
    if len(ret)==0:
        return None
    else:
        return ret

def cursor_to_dict(f1,retrieve):
    l=[]
    for f in f1:
        l.append(f)

    ret=[]
    for a in l:
        dic={}
        for key in retrieve.keys():
            steps=key.split('.')
            partial_res=a
            for step in steps:
                partial_res=partial_res.get(step)
                if partial_res==None: break
                if type(partial_res)==type([]):
                    partial_res=None
                    break

            legend_to_show=key.split('.')[-1]
            if (legend_to_show=="file_id"):legend_to_show="sha1"

            if (legend_to_show=="TimeDateStamp" and partial_res!=None):partial_res=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(int(eval(partial_res),16)))
            if (legend_to_show=="timeDateStamp" and partial_res!=None):partial_res=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(partial_res))

            dic[legend_to_show]=partial_res

        ret.append(dic)
    return ret


#****************TEST_CODE******************
import os
import time

TEST="-test_Functions"
def testCode():
    print("*****ENTROPY*****")

    dir=os.getcwd()
    file=dir+"//test.exe"
    start_time=time.time()
    f=open(file,"rb")
    data=f.read()
    elapsed_read=time.time()-start_time

    print("File size: "+ str(len(data)))
    print("Read time: " + str(elapsed_read) + " --- Time per byte: "+ str(elapsed_read/len(data)))
    print("Entropy calculation time: "+ str(elapsed_entropy)+" --- Time per byte: "+ str(elapsed_entropy/len(data)))
    print("")
    print("Read time GB:    "+str((1073741824/len(data))*elapsed_read))
    print("Entropy time GB: "+str((1073741824/len(data))*elapsed_entropy))

    print("")
    print("Entropy file: "+str(res))


    file=dir+"//testComp.exe"
    f=open(file,"rb")
    data=f.read()
    res=getEntropy(data)
    print("Entropy file paq: "+str(res))

    pass


#***********************TEST***************************
import sys
import traceback
if(len(sys.argv)>=2):
    if(sys.argv[1]==TEST):
        try:
            print("######## Test of " + str(sys.argv[0])+" ########")
            testCode()

        except:
            print(traceback.format_exc())
        raw_input("Press a key...")
