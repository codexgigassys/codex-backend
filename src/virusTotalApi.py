# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import requests
import hashlib
import traceback

from MetaControl.MetaController import *
from secrets import env


def download_from_virus_total(file_id):
    print "download_form_virus_total(): "+str(file_id)
    apikey = env["vt_apikey"]
    params = {'apikey':apikey,'hash':file_id}
    try_again = True
    fail_count=0
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

def parse_vt_response(json_response):
    #print(json_response)
    response_code=json_response.get("response_code")
    if(response_code!=1): return None
    sha1=json_response.get("sha1")
    positives=json_response.get("positives")
    total=json_response.get("total")
    scan_date=json_response.get("scan_date")


    vt_scans=json_response.get("scans")
    ret_scans=[]
    if(vt_scans!=None):
        for key in vt_scans.keys():
            av_dict=vt_scans[key]
            av_dict["name"]=key
            ret_scans.append(av_dict)

    ret={}
    ret["sha1"]=sha1
    ret["positives"]=positives
    ret["total"]=total
    ret["date"]=scan_date
    ret["scans"]=ret_scans

    #print(ret)
    return ret


def get_vt_av_result(file_id):
    apikey=env["vt_apikey"]
    params = {'apikey':apikey,'resource':file_id}
    try:
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    except Exception, e:
        print str(e)
        return None
    parsed_response = parse_vt_response(response.json())
    try:
        parsed_response = parse_vt_response(response.json())
    except Exception, e:
        print "response.json() error. get_vt_av_result("+str(file_id)+")"
        print str(e)
        print "response="+str(response)
        return None
    return parsed_response

def get_av_result(file_id):
    #buscar si ya existe
    mdc=MetaController()
    analysis_result=mdc.search_av_analysis(file_id)

    if analysis_result==None:
        print("Buscando analysis de %s en VT" % file_id)
        analysis_result=get_vt_av_result(file_id)
        #guardar en la base de datos
        if(analysis_result==None): return None
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

