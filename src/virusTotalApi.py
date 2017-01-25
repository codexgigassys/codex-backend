# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import requests
import hashlib
import traceback
import logging

from MetaControl.MetaController import *
from PackageControl.PackageController import *
from KeyManager.KeyManager import KeyManager
try:
    from config.secrets import env
except ImportError:
    from config.default_config import env
from Utils.Functions import key_list_clean,key_dict_clean,rec_key_replace,process_file,valid_hash
from Utils.ProcessDate import process_date
import time


#Walk through a dictionary structure
def read_from_dictionary(source,dic):
    path = source.split('.')
    root = dic
    for p in path:
        try:
            root = root.get(p)
            if(root == None): return None
        except Exception, e:
            print str(e)
            return None
    return root

# Given a hash, it downloads the file from VirusTotal
# it checks that the downloaded file correspond to the
# hash. Returns the binary data of the file.
def download_from_virus_total(file_id):
    logging.debug("download_from_virus_total(): "+str(file_id))
    if not valid_hash(file_id):
        raise ValueError("download_from_virus_total recieved an invalid hash")
    key_manager = KeyManager()
    #apikey = env["vt_private_apikey"]
    has_key = False
    while not has_key:
        apikey = key_manager.get_key('download_sample')
        if(apikey.get('key') is None and apikey.get('timeleft') is None):
            return None
        elif apikey.get('key') is not None:
            has_key = True
        elif((isinstance(apikey.get('timeleft'),int) or
                isinstance(apikey.get('timeleft'),float)) and
                apikey.get('timeleft') > 0):
            logging.debug("download_from_virus_total(): timeleft="+str(apikey.get('timeleft')))
            time.sleep(apikey.get('timeleft'))

    params = {'apikey': apikey.get('key'),'hash':file_id}
    try_again = True
    fail_count=0
    response = None
    while(try_again):
        try:
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/download', params=params, timeout = 30)
            try_again=False
        except Exception, e:
            logging.exception("requests to virustotal / download")
            #print(str(e))
            #print(traceback.format_exc())
            try_again=True
            fail_count+=1
            if(fail_count >= 3):
                break
    if(response is None):
        return {"status": None, "file": None}
    if(response.status_code == 200):
        downloaded_file = response.content
        largo=len(file_id)
        if(largo==32):
            check=hashlib.md5(downloaded_file).hexdigest()
        elif(largo==40):
            check=hashlib.sha1(downloaded_file).hexdigest()
        elif(largo==64):
            check=hashlib.sha256(downloaded_file).hexdigest()

        if(check!=file_id):
            logging.warning("download_from_virus_total(): check!="+str(file_id))
            return {"status": "invalid_hash", "file": None}
        else:
            return {"status": "ok", "file": downloaded_file}
    elif(response.status_code == 204):
        key_manager.block_key(apikey.get('key'))
        return {"status": "out_of_credits", "file": None}
    elif(response.status_code == 403):
        logging.error("params="+str(params))
        logging.error("apikey="+str(apikey.get('key')))
        return {"status": "invalid_key", "file": None}
    elif(response.status_code == 404):
        return {"status": "not_found", "file": None}
    else:
        logging.error( "download_from_virus_total(): status_code="+str(response.status_code)+". ("+str(file_id)+")")
        return {"status": response.status_code, "file": None}

# Recieves VT scans dictionary
# and returns number of AV
# that detect the sample as
# malware.
def total_positive(vt_dict):
    if vt_dict is None:
        return None
    count=0
    for x in vt_dict:
        if x.get('detected'):
            count+=1
    return count

# Recieves the full VT response
# it translate the antivirus scans
# from a dictionary to an array
# in order to be able to search
# by AV name. The same with imports.
# When VT request includes
# allinfo: 1, parameters total, and positives
# are missing, but can be calculated manually.
def parse_vt_response(json_response):
    if json_response is None:
        logging.exception("parse_vt_response recieved None")
        raise ValueError("json_response is None")
    response_code=json_response.get("response_code")
    if(response_code!=1):
        return None

    positives=json_response.get("positives")
    total=json_response.get("total")

    if positives is None and json_response.get('scans') is not None:
        positives = total_positive(json_response.get('scans'))
        total = len(json_response.get('scans'))

    # scans uses antivirus as json key, and
    # imports uses dll's as keys. So they can't be saved
    # to mongo or seached easily. So we convert the dictionary (of scans)
    # and the array (of imports) into an array
    # dictionaries, where the key is now in 'name'.
    if json_response.get('scans') is not None:
        json_response["scans"]=key_dict_clean(json_response["scans"])
    if json_response.get('additional_info') is not None and json_response.get('additional_info').get('imports') is not None:
        json_response["additional_info"]["imports"]=key_list_clean(json_response["additional_info"]["imports"])
    if json_response.get('additional_info') is not None and json_response.get('additional_info').get('pe-resource-types') is not None:
        json_response["additional_info"]["pe-resource-types"] = key_list_clean(json_response["additional_info"]["pe-resource-types"])
    json_response = rec_key_replace(json_response)
    ret = json_response
    ret["positives"]=positives
    ret["total"]=total
    
    #Trying to get the best date
    date_registers = ['first_seen','additional_info.first_seen_itw','scan_date']
    for register in date_registers:
        vt_date = read_from_dictionary(register,json_response)
        if vt_date != None: break
    
    try:
        #The "date" value is use to speed up time queries for av signatures
        ret["date"] = process_date(vt_date)        
    except ValueError:
        ret["date"] = None
        logging.exception("virusTotalApi->parse_vt_response: invalid date recieved by VT: "+str(vt_date))
    
    return ret

# Request the VT data for a given hash
# and converts the json response to a python
# dictionary. In case of error, returns None.
def get_vt_av_result(file_id,priority="low"):
    key_manager = KeyManager()
    has_key = False
    while not has_key:
        apikey = key_manager.get_key('av_analysis',priority)
        if(apikey.get('key') is None and apikey.get('timeleft') is None):
            return None
        elif apikey.get('key') is not None:
            has_key = True
        elif apikey.get('key') is None and priority == "high":
            return {"status": "no_key_available"}
        elif(((isinstance(apikey.get('timeleft'),int) or
                isinstance(apikey.get('timeleft'),float))) and
                apikey.get('timeleft') > 0):
            time.sleep(apikey.get('timeleft'))

    params = {'apikey':apikey.get('key'),'resource':file_id, 'allinfo': '1'}
    try:
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params, timeout = 30)
    except Exception, e:
        logging.exception("VT /report request. "+str(e))
        return {"status": "error", "error_message": str(e), "response": None}
    if response.status_code == 200:
        try:
            parsed_response = response.json()
        except Exception, e:
            logging.exception("response.json() error. get_vt_av_result("+str(file_id)+")"+"e="+str(e))
            logging.info("response="+str(response))
            return {"status": "error", "error_message": "Error when parsing response"}
        logging.debug("get_vt_av_result-->=200")
        if parsed_response.get('response_code')==1:
            return {"status": "ok", "response": parsed_response}
        elif parsed_response.get('response_code')==0:
            return {"status": "not_found", "response": parsed_response}
        else:
            logging.debug("response="+str(parsed_response))
            return {"status": "error", "error_message": "Error in av_analysis. HTTP status 200, but response_code="+str(parsed_response.get('response_code')), "response": parsed_response}
    elif respone.status_code == 204:
        logging.info("get_vt_av_result-->204")
        #raise ValueError("Out of credits when trying to download av_result. Someone else is using the same API key?")
        return {"status": "out_of_credits", "response": None}
    elif response.status_code == 403:
        return {"status": "error", "error_message": "VT returned 403 for av_analysis (invalid key?)", "response": None}
    elif response.status_code == 404:
        logging.error( "get_vt_av_result-->404")
        return {"status": "error", "error_message": "VT returned 404 for av_analysis", "response": None}
    else:
        logging.error("get_vt_av_result-->error")
        return {"status": "error", "status_code": response.status_code, "error_message": "in get_vt_av_result: response.status_code="+str(response.status_code), "response": None}



# Returns a dictionary with:
# * scans: Antivirus scan result for a given hash.
# * status:
#       - added: when VT was downloaded
#       - ok: when was already in the DB
#       - out_of_credits:
#       - error
def get_av_result(file_id,priority="low"):
    if not valid_hash(file_id):
        raise ValueError("Invalid hash")

    mdc=MetaController()
    analysis_result=mdc.search_av_analysis(file_id)
    added=False
    status = None
    if analysis_result==None:
        logging.info("Searching analysis of %s in VT" % file_id)
        vt_av_result = get_vt_av_result(file_id,priority)
        status = vt_av_result.get('status')
        if vt_av_result.get('status') == "ok":
            vt_av_result_response = vt_av_result.get('response')
            analysis_result=parse_vt_response(vt_av_result_response)
            # Save in mongo
            if(analysis_result is not None):
                logging.info( "saving vt av from "+str(file_id)+ " in mongo")
                mdc.save_av_analysis(file_id,analysis_result)
            status = "added"
        elif vt_av_result.get('status') == "error":
            return {"scans": None, "hash": file_id, "status": "error", "error_message": vt_av_result.get('error_message')}
    else:
        status = "already_had_it"

    if analysis_result is not None:
        scans=analysis_result.get("scans")
        positives = analysis_result.get('positives')
        total = analysis_result.get('total')
    else:
        positives = 0
        total = 0
        scans = None
    response = {"scans": scans, "positives": positives,
            "total": total, "hash": file_id, "status": status}
    return response

def save_file_from_vt(hash_id):
    downloaded_file=download_from_virus_total(hash_id)
    if(downloaded_file==None):
        return {"status": "unknown", "hash": None}
    if downloaded_file.get('status') == "out_of_credits":
        return {"status": "out_of_credits", "hash": None}
    if downloaded_file.get('status') == "not_found":
        return {"status": "not_found", "hash": None}
    if downloaded_file.get('status') == 'ok':
        data_bin=downloaded_file.get('file')
        file_id=hashlib.sha1(data_bin).hexdigest()
        pc=PackageController()
        res=pc.searchFile(file_id)
        if(res==None): # File not found. Add it to the package.
            pc.append(file_id,data_bin,True)
            return {"status": "added", "hash": file_id}
        else:
            process_file(file_id)
            return {"status": "inconsistency_found", "hash": file_id}

def test():
    file_id="8260795f47f284889488c375bed2996e"
    data=download_from_virus_total(file_id)
    if(data==None):
        print("File not found OK")
    else:
        print("File not found ERROR")

    file_id="d41d8cd98f00b204e9800998ecf8427e"
    data=download_from_virus_total(file_id)
    if(data==""):
        print("File found OK")
    else:
        print("File found ERROR")

    return

def test2():
    hash="1df6ae2a5594ab29a6e60b6d9296128b1f9fd980" #stuxnet
    #hash="8260795f47f284889488c375bed2996e" # does not exist
    res=get_av_result(hash)
    print(res)

if __name__ == "__main__":
    test2()

