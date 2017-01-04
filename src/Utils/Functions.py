# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
from db_pool import *
#from IPython import embed
import re
from datetime import datetime as dtdatetime,timedelta
import subprocess
from PackageControl.PackageController import *
from MetaControl.MetaController import *
from Sample import *
from Launcher import *
import csv
import json
import string
import random
import re


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

def number_of_jobs_on_queue(queue_name):
    w=re.match("^[a-z]+$",queue_name)
    if(w is None):
        raise ValueError("invalid queue_name")
    command = ["bash","-c","rq info --url redis://"+env.get('redis').get('host')+":"+str(env.get('redis').get('port'))+" --raw | grep -E -e \"^queue "+queue_name+" [0-9]+$\" | sed \"s/queue "+queue_name+" //g\" | tr -d \"\\n\""]
    output = call_with_output(command)
    print "output="+str(output)
    try:
        return int(output)
    except ValueError,e:
        print "ValueError in int(output): "+str(e)
        return 0

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
        if isinstance(s,(int,long)):
            return str(s)+" ("+str(hex(s))+")"
        else:
            return s
    elif isinstance(s,dtdatetime):
        return str(s)
    elif s is None:
        return s
    else:
        if(is_iterable(s) and not is_printable(s)):
            return display_with_hex(s)
        else:
            return str(s)
    print str(s)
        #embed()
    return s

def vt_key():
    return env.get('vt_apikey') is not None and type(env.get('vt_apikey'))==str and len(env.get("vt_apikey"))>5

# This function recives a dictionary like
# {"key1": { "something": 1},
#  "key2": { "something": 2}}
# and returns
# [ {"name": "key1", "something": 1 },
#   {"name": "key2", "something": 2 }]
# This is useful for converting the format
# VirusTotal API sends the AV scans into
# something easily searchable by mongo.
def key_dict_clean(json):
    if json is None:
        return None
    array=[]
    for key in json.keys():
        tmp_dict=json.get(key)
        tmp_dict["name"]=key
        array.append(tmp_dict)
    return array

# Replace dot with _
# in dictionaries keys
# in order to save them in mongo
def rec_key_replace(obj):
	if isinstance(obj, dict):
		return {key.replace('.', '_'): rec_key_replace(val) for key, val in obj.items()}
	return obj

# This functions recieves a dictionary like
# {"key1": ["something1", "something2"],
#  "key2": ["something1", "something2"]}
# and returns
# [ {"name": "key1", "values": ["something1, something2"]},
# {"name": "key2", "values": ["something1, something2"]} ]
# This is useful for converting the format
# VirusTotal API sends the imports into
# something easily searchable by mongo.
def key_list_clean(json):
    if json is None:
        return None
    array=[]
    for key in json.keys():
        tmp_dict={}
        tmp_dict["name"]=key
        tmp_dict["values"]=json.get(key)
        array.append(tmp_dict)
    return array

def to_bool(string):
    if string is None:
        return False
    string=string.strip().lower()
    if string=="false" or string is None:
        return False
    else:
        return bool(string)


def jsonize(data):
    return json.dumps(data, sort_keys=False, indent=4)


# Checks if the meta has a date. If it doesn't
# it updates it. If a date is found, the oldest
# date will get saved.
def update_date(file_id,date):
    if file_id is None or date is None:
        return
    mdc=MetaController()
    res=mdc.save_first_seen(file_id,date)

def log_event(event,file_hash,comments=""):
    with open("logs.csv","a+") as logfile:
        csv_writer=csv.writer(logfile)
        csv_writer.writerow([str(dtdatetime.now().isoformat()),str(event),str(file_hash),str(comments)])


def change_date_to_str(res):
    if res is None:
        return None
    for date_key in ["date","upload_date","date_start", "date_end", "date_enqueued"]:
        if res.get(date_key) is None:
            pass
        else:
            res[date_key]=str(res.get(date_key))
    return res


def process_file(file_hash,force=False):
    if not is_sha1(file_hash):
        raise ValueError("process_file only accepts sha1")
    print "process_file("+str(file_hash)+")"
    pc=PackageController()
    res=pc.getFile(file_hash)
    if res==None:
        print "Error: process_file("+str(file_hash)+"): pc.getFile returned None"
        return None
    sam_id=file_hash
    sample=Sample()
    sample.setID(sam_id)
    sample.setBinary(res)
    if force:
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
        if m is None:
            return ""
        else:
            return m.group(0)




#returns true if a hash is md5 or sha1 valid. False otherwise
def valid_hash(hash):
    return hash is not None and (len(hash)==32 or len(hash)==40 or len(hash)==64 or len(hash)==128) and re.search('^[a-f0-9]+$',hash) is not None


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
    elif len(hash)==64:
        ret = search_by_hash_and_type(hash,"sha2")
    if ret is not None and ret[0] is not None:
        return ret[0].get('hash').get('sha1')
    else:
        return None

# Given a hash and a type (md5 or file_id (sha1))
# it will search in meta collection.
def search_by_hash_and_type(hash,type):
    if type is not "md5" and type is not "sha1" and type is not "sha2":
        raise ValueError("type is not valid. (search_by_hash_and_type)")
        return None
    search={'$and': [{'hash.'+type: hash}]}
    retrieve={'hash.sha1': 1}
    coll_meta=db.meta_container
    f1=coll_meta.find(search,retrieve).limit(1)

    if f1.count() ==0:
        return None
    else:
        return f1

# Check the format of
# a textarea hashes.
# (string with \n's)
def check_hashes(hashes):
    errors = []
    result_hashes = []
    for hash_id in hashes.split("\n"):
        hash_id = clean_hash(hash_id)
        if hash_id is None:
            continue
        if(not valid_hash(hash_id)):
            errors.append({"error": 5, "error_message": "invalid_hash: " + str(hash_id) })
        else:
            result_hashes.append(hash_id)
    return {"hashes": result_hashes, "errors": errors}

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def add_error(resp_dict,error_code,error_message):
    if type(resp_dict) != dict:
        return resp_dict
    if resp_dict.get('errors') is None:
        resp_dict["errors"] = []
    resp_dict["errors"].append({"code": error_code, "message": error_message })
    return resp_dict


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
