# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import requests
import hashlib
import traceback

from MetaControl.MetaController import *
try:
    from config.secrets import env
except ImportError:
    from config.default_config import env
from Utils.Functions import key_list_clean,key_dict_clean


def download_from_virus_total(file_id):
    print "download_form_virus_total(): "+str(file_id)
    apikey = env["vt_apikey"]
    if(len(apikey)==0):
        return None
    params = {'apikey':apikey,'hash':file_id}
    try_again = True
    fail_count=0
    response = None
    while(try_again):
        try:
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/download', params=params)
            try_again=False
        except Exception, e:
            print(str(e))
            print(traceback.format_exc())
            try_again=True
            fail_count+=1
            if(fail_count >= 3):
                break
    if(response is None):
        return
    if(response.status_code == 200):
        downloaded_file = response.content
        largo=len(file_id)
        if(largo==32):
            check=hashlib.md5(downloaded_file).hexdigest()
        elif(largo==40):
            check=hashlib.sha1(downloaded_file).hexdigest()
        elif(largo==64):
            check=hashlib.sha256(downloaded_file).hexdigest()
        else: return None
        if(check!=file_id):
            print "download_from_virus_total(): check!="+str(file_id)
            return None
        return downloaded_file

    else:
        print "download_from_virus_total(): status_code="+str(response.status_code)+". ("+str(file_id)+")"
        return None

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
        return None
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

    ret = json_response
    ret["positives"]=positives
    ret["total"]=total
    return ret

# Request the VT data for a given hash
# and converts the json response to a python
# dictionary. In case of error, returns None.
def get_vt_av_result(file_id):
    apikey=env["vt_apikey"]
    if(len(apikey)==0):
        return None
    params = {'apikey':apikey,'resource':file_id, 'allinfo': '1'}
    try:
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    except Exception, e:
        print str(e)
        return None
    try:
        parsed_response = response.json()
    except Exception, e:
        print "response.json() error. get_vt_av_result("+str(file_id)+")"
        print str(e)
        print "response="+str(response)
        return None
    return parsed_response

# Returns the Antivirus scan result for a given hash.
def get_av_result(file_id):
    mdc=MetaController()
    analysis_result=mdc.search_av_analysis(file_id)
    #analysis_result = None #while we test VT function

    if analysis_result==None:
        print("Searching analysis of %s in VT" % file_id)
        analysis_result=parse_vt_response(get_vt_av_result(file_id))
        # Save in mongo
        if(analysis_result==None):
            return None
        mdc.save_av_analysis(file_id,analysis_result)

    scans=analysis_result.get("scans")
    for s in scans:
        av_name=s.get("name")
        if(av_name=="ESET-NOD32" or av_name=="NOD32" or av_name=="NOD32v2"):
            type=s.get("result")
            positives=analysis_result.get("positives")
            total=analysis_result.get("total")
            return (type,positives,total)

    return None

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

