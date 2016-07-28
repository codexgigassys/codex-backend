#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
import gevent
import os
import json
import copy
import argparse
import tempfile
import time
from datetime import datetime as dtdatetime
import csv
from czipfile import ZipFile
import subprocess
from Sample import *
from bottle import route, request, response, run, hook, get, HTTPError, BaseRequest, static_file, response
BaseRequest.MEMFILE_MAX = 2147483646
from PackageControl.PackageController import *
from MetaControl.MetaController import *
from Launcher import *
from Query.apifuzz import *
import tree_menu
from bson import Binary,Code
from bson.json_util import dumps
import SearchModule
from virusTotalApi import download_from_virus_total,get_av_result
import string
import random
from IPython import embed
from rq import Queue
from redis import Redis
from Utils.Functions import call_with_output,clean_hash,process_file,log_event,recursive_read
import re
from Utils.InfoExtractor import *
from loadToMongo import *
import cgi

tmp_folder="/tmp/mass_download/"

def add_hash_to_process_queue(sha1):
    q = Queue('process',connection=Redis())
    job = q.enqueue('process_hash.generic_process_hash',args=(sha1,),timeout=70)


def add_list_to_process_queue(res):
    if type(res)==list:
        for sample in res:
           add_hash_to_process_queue(sample.get('sha1')) 

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def jsonize(data):
    return json.dumps(data, sort_keys=False, indent=4)

def jsonp(data,callback):
    reply = {"status": "OK", "data": data}
    return callback+"(["+jsonize(reply)+"]);"

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    

@route('/api/v1/av_result', method='OPTIONS')
def enable_cors_for_process():
    return 0

@route('/api/v1/process', method='OPTIONS')
def enable_cors_for_process():
    return 0

@route('/api/v1/process_debug', method='OPTIONS')
def enable_cors_for_process():
    return 0

@route('/api/v1/yara', method='OPTIONS')
def enable_cors_for_yara():
    return 0

@route('/api/v1/download', method='OPTIONS')
def enable_cors_for_download():
    return 0

@route('/api/v1/check_imp', method='OPTIONS')
def enable_cors_for_check_imp():
    return 0

@route('/api/v1/check_lib', method='OPTIONS')
def enable_cors_for_check_lib():
    return 0

@get('/favicon.ico')
def get_favicon():
    return static_file("icon.png","./WEB") 

@route('/api/test', method='GET')
def test():
    enable_cors()
    return jsonize({'message' : 'Server Runing'})
    
@route('/api/v1/search_tree', method='GET')
def search_tree():
    return jsonize(tree_menu.tree)

@route('/api/v1/status_files_to_load', method='GET')
def api_status_files_to_load_folder():
    path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','files_to_load'))
    files=recursive_read(path)
    return str(len(files))+" files in files_to_load folder."

    
@route('/api/v1/load_to_mongo', method='GET')
def api_load_to_mongo():
    path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','files_to_load'))
    print path
    return load_to_mongo2(path)

@get('/api/v1/samples')
def get_sample_count():
    count=SearchModule.count_documents()
    res={"count":count}
    return jsonize(res)

@route('/api/v1/metadata', method='GET')
def get_metadata():
    file_hash=clean_hash(request.query.file_hash)
    if file_hash is None:
        return
    if len(file_hash) == 32: #ToDo: validate hash
        key = 'md5'
    elif len(file_hash) == 40:
       key = 'sha1'
    #elif len(file_hash) == 64:
    #   key = 'sha256'
    else:
        response.code = 400
        return jsonize({'message':'Invalid hash format (use MD5, SHA1 or SHA2)'})
    
    mdc=MetaController()
    res=mdc.read(file_hash)
    if res==None:
        response.code = 404
        return jsonize({'message':'Metadata not found in the database'})
    log_event("metadata",file_hash)
    
    return dumps(res)


@route('/api/v1/logs', method='GET')
def logs():
    try:
        csvfile = open('logs.csv','r')
    except Exception, e:
        print str(e)
        return jsonize([])
        
    fieldnames = ("datetime","message","hash","comments")
    reader = csv.DictReader( csvfile, fieldnames)
    l=[row for row in reader ]
    l=l[::-1]
    l=l[0:100]
    out = json.dumps(l)
    return out
 
@route('/api/v1/process', method='GET')
def api_process_file():
    file_hash=clean_hash(request.query.file_hash)
    if len(file_hash) != 40:
        response.code = 400
        return jsonize({'message':'Invalid hash format (use sha1)'})
    
    res=process_file(file_hash)
    if res==None:
        response.code = 404
        return jsonize("File not found in the database")
    
    return jsonize("File processed")
 
@route('/api/v1/search', method='GET')
def search():   
    data=request.query.data
    str_lim=request.query.limit
    columns=request.query.getall("selected[]")
    #print(request.query.keys())
    print(columns)
    if(str_lim==''):
        limit=0
    else:
        limit=int(str_lim)
    callback_name = cgi.escape(request.query.callback)
    print "callback="+str(callback_name)
    res=SearchModule.search_by_id(data,limit,columns)
    add_list_to_process_queue(res[0:10]) 
    
    #para que muestre solo algunas columnas (gronchada)
    if(len(columns)==0):
        show=["sha1","description","size"]
    else:
        show=["sha1"]
        for col in columns:
            dic=tree_menu.ids[int(col)]
            path=str(dic["path"]).split('.')[-1]
            show.append(path)
    
    responsex={}
    responsex["normal"]=res
    responsex["show"]=show
        
    return jsonp(responsex,callback_name)

@route('/api/v1/download', method='POST')
def get_package_file():
    tmp_folder="/tmp/mass_download"
    subprocess.call(["mkdir","-p",tmp_folder]) 
    hashes = request.forms.dict.get("file_hash[]")
    if hashes is None:
        hashes = request.forms.get("file_hash").split("\n")
    if hashes is not None:
        if len(hashes) == 1:
            random_id=hashes[0]
        else:
            random_id = id_generator()
    else:
        return jsonize({'message':'Error. no file selected'})
    folder_path=os.path.join(tmp_folder,random_id)
    subprocess.call(["mkdir","-p",folder_path]) 
    zip_name=os.path.join(tmp_folder,random_id+".zip")
    
    pc=PackageController()
    
    for file_hash in hashes:
        file_hash = clean_hash(file_hash.replace('\r',''))
        
        data="1="+file_hash
        res=SearchModule.search_by_id(data,1)
        if(len(res)==0):
            pass
        else:    
            file_hash=res[0]["sha1"]
                
        res=pc.searchFile(file_hash)
        if res != 1 and res is not None:
            res=pc.getFile(file_hash) 
            file_name=os.path.join(folder_path,str(file_hash)+".codex")
            fd=open(file_name,"wb")
            fd.write(res)
            fd.close()
        elif res == 1:
            fd=open(os.path.join(folder_path,'readme.txt'),'a+')
            fd.write(str(file_hash)+" is not available to download.\n")
            fd.close()
        elif res is None:
            fd=open(os.path.join(folder_path,'readme.txt'),'a+')
            fd.write(str(file_hash)+" not found.")
            fd.close()
        else:
            print "Unknown res:"+str(res)
    
    subprocess.call(["zip","-P","codex","-jr", zip_name,folder_path])
    resp =  static_file(str(random_id)+".zip",root=tmp_folder,download=True)
    resp.set_cookie('fileDownload','true');
    # http://johnculviner.com/jquery-file-download-plugin-for-ajax-like-feature-rich-file-downloads/
    return resp

    
@route('/api/v1/file/get', method='GET')
def get_file():
    tmp_folder="/tmp/mass_download"
    subprocess.call(["mkdir","-p",tmp_folder]) 
    file_hash = clean_hash(request.query.file_hash)
    key = ''
    if len(file_hash) == 40:
        key = 'sha1'
    else:
        response.code = 400
        return jsonize({'message':'Invalid hash format (use sha1)'})
        
    pc=PackageController()
    res=pc.searchFile(file_hash)
    
    if res==None:
        response.code = 404
        return jsonize({'message':'File not found in the database'})
    if res==1:
        response.code = 400
        return jsonize({'message':'File not available for downloading'})
    res=pc.getFile(file_hash) 
    zip_name=os.path.join(tmp_folder,str(file_hash)+'.zip')
    file_name=os.path.join(tmp_folder,str(file_hash)+'.codex')
    fd=open(file_name,"wb")
    fd.write(res)
    fd.close()
    subprocess.call(["zip","-ju","-P","codex",zip_name,file_name])
    return static_file(str(file_hash)+".zip",root=tmp_folder,download=True)

@route('/api/v1/file/add', method='OPTIONS')
def add_file_options():
    return "OK"


def upload_file(data_bin):
    pc=PackageController()
    file_id=hashlib.sha1(data_bin).hexdigest()
    res=pc.searchFile(file_id)
    if(res==None): # File not found. Add it to the package.
        pc.append(file_id,data_bin)
        print("Added: %s" % (file_id,))
        log_event("file added",str(file_id))
        return "ok"
    else:
        if(res==0):#file already exists
            log_event("file already exists",str(file_id))
            return "already exists"
        else:#existe y esta bloqueado por vt
            log_event("file already exists",str(file_id))
            return "virustotal"

          

@route('/api/v1/file/add', method='POST')
def add_file():
    #tags = request.forms.get('name')
    upload = request.files.get('file')
    name = upload.filename
    data_bin=upload.file.read()
    file_id=hashlib.sha1(data_bin).hexdigest()
    print "file_id="+str(file_id)
    status=upload_file(data_bin)
    process_file(file_id) #ToDo: add a redis job
    if(status == "ok"):
        return jsonize({'message': 'Added with '+str(file_id)})
    elif(status == "already exists"):
        return jsonize({'message': 'Already exists '+str(file_id)})
    elif(status == "virustotal"):
        return jsonize({'message': 'Already exists '+str(file_id)})
    else:
        return jsonize({'message': 'Error'})

@route('/api/v1/yara', method='POST')
def yara():
    tmp_folder="/tmp/yara_working_dir"
    subprocess.call(["mkdir","-p",tmp_folder]) 
    hashes = request.forms.dict.get("file_hash[]")
    if hashes is not None:
        if len(hashes) == 1:
            random_id=hashes[0]
        else:
            random_id = id_generator()
    else:
        return jsonize({'message':'Error. no file selected'})
    folder_path=os.path.join(tmp_folder,random_id)
    subprocess.call(["mkdir","-p",folder_path]) 
    yara_output_file=os.path.join(tmp_folder,random_id+".txt")
    for file_hash in hashes:
        key = ''
        if len(file_hash) == 40:
            key = 'sha1'
        else:
           response.code = 400
           return jsonize({'message':'Invalid hash format (use sha1)'})
        
        pc=PackageController()
        res=pc.searchFile(file_hash)
        if res==None:
            response.code = 404
            return jsonize({'message':'File not found in the database'}) #needs a better fix
        res=pc.getFile(file_hash) 
    
        file_name=os.path.join(folder_path,str(file_hash)+".codex")
        if not os.path.isfile(file_name):
            fd=open(file_name,"wb")
            fd.write(res)
            fd.close()
    yara_cli_output = call_with_output(["python",env['yara-script2'],"--opcodes","--excludegood","--nosimple","-z","5","-m",folder_path,"-o", yara_output_file])
    #yara_cli_output = call_with_output(["python",env['yara-script1'],"-f","exe","-a","Codex Gigas","-r",yara_output_file, folder_path+"/"])
#    yara_output_file += ".yar" # because the script yara-script2 is ugly and saves the file to x.yar.yar 
    if os.path.isfile(yara_output_file) is False:
        fp = open(yara_output_file,'w+')
        fp.write(yara_cli_output)
        fp.close()
    yara_output_fp = open(yara_output_file,'r')
    output_cleaned = yara_output_fp.read().replace("[!] Rule Name Can Not Contain Spaces or Begin With A Non Alpha Character","")
    output_cleaned = re.sub(r"\[\+\] Generating Yara Rule \/tmp\/yara_working_dir\/[A-Z0-9]+\.txt from files located in: /tmp/yara_working_dir/[A-Z0-9]+/","",output_cleaned) 
    output_cleaned = re.sub(r"rule /tmp/yara_working_dir/([a-zA-Z0-9]+).txt",r"rule \1",output_cleaned)
#    lines = [line for line  in output_with_credits_removed if line.strip()]
    return jsonize({"message": output_cleaned})

@route('/api/v1/process_debug', method='POST')
def api_batch_process_debug_file():
    yield "<html><body><pre>"
    yield "Running Batch process\n"
    file_hashes=request.forms.get('file_hash')
    #print(dir(request.forms))
    #print(request.forms.keys())
    #transformar file_hashes a una lista de hashes
    not_found=[]
    added_to_queue=0
    downloaded_from_vt=0
    for hash_id in file_hashes.split("\n"):
        hash_id=clean_hash(hash_id)
        if hash_id is None:
            continue
        data="1="+hash_id
        res=SearchModule.search_by_id(data,1,[],False)
        if(len(res)==0):
            print "downloading "+str(hash_id)+" from vt"
            sha1=SearchModule.add_file_from_vt(hash_id)
            if(sha1==None):
                not_found.append(hash_id)
                continue
            else:
                downloaded_from_vt+=1
        else:    
            sha1=res[0]["sha1"]

        added_to_queue+=1    
        add_hash_to_process_queue(sha1)
	yield str(sha1)+"\n"
   
    responsex=str(added_to_queue)+" files added to the process queue.\n"
    if(downloaded_from_vt > 0):
        responsex+=str(downloaded_from_vt)+" new hashes.\n"
    if(len(not_found)!=0):
        responsex+=str(len(not_found))+ " hashes not found.\n"
        responsex+="Not Found:\n"
        for aux in not_found:
            responsex=responsex+str(aux)+"\n"
    yield responsex
    yield "END"

@route('/api/v1/process', method='POST')
def api_batch_process_file():
    print("Running Batch process")
    file_hashes=request.forms.get('file_hash')
    #print(dir(request.forms))
    #print(request.forms.keys())
    #transformar file_hashes a una lista de hashes
    not_found=[]
    added_to_queue=0
    downloaded_from_vt=0
    for hash_id in file_hashes.split("\n"):
        hash_id=clean_hash(hash_id)
        if hash_id is None:
            continue
        data="1="+str(hash_id)
        res=SearchModule.search_by_id(data,1,[],False)
        if(len(res)==0):
            not_found.append(hash_id)
            continue
            """
            print "downloading "+str(hash_id)+" from vt"
            sha1=SearchModule.add_file_from_vt(hash_id)
            if(sha1==None):
                print "not found on vt: "+str(hash_id)
                not_found.append(hash_id)
                continue
            else:
                downloaded_from_vt+=1
            """
        else:    
            sha1=res[0]["sha1"]

        added_to_queue+=1    
        print str(hash_id)+" added to queue"
        add_hash_to_process_queue(sha1)
   
    responsex=str(added_to_queue)+" files added to the process queue.\n"
    if(downloaded_from_vt > 0):
        responsex+=str(downloaded_from_vt)+" new hashes.\n"
    if(len(not_found)!=0):
        responsex+=str(len(not_found))+ " hashes not found.\n"
        responsex+="Not Found:\n"
        for aux in not_found:
            responsex=responsex+str(aux)+"\n"
    
    return jsonize({"message":responsex}) 

    
@route('/api/v1/check_lib', method='GET')
def check_lib():
    lib=str(request.query.q)
    mdc=MetaController()
    res=mdc.searchDllByName("'"+lib.lower()+"'")
    
    if(res!= None):
        return jsonize({"valid":True})
    else:
        return jsonize({"valid":False})
        
@route('/api/v1/check_imp', method='GET')
def check_imp():
    imp=str(request.query.q)
    mdc=MetaController()
    res=mdc.searchImportByName("'"+imp.lower()+"'")
    
    if(res!= None):
        return jsonize({"valid":True})
    else:
        return jsonize({"valid":False})

@route('/api/v1/export', method='POST')
def export_metadata():
    mdc=MetaController()
    hashes = request.forms.dict.get("file_hash[]")
    dump_to_save=""
    for hash in hashes:
        hash = clean_hash(hash.replace('\r',''))
    
        res=mdc.read(hash)
        dump=dumps(res,indent=4)
        line="\n\n#### File:%s\n"%hash
        dump_to_save=dump_to_save+line+dump
    
    id_random=id_generator()
    
    tmp_folder="/tmp/meta_export"
    subprocess.call(["mkdir","-p",tmp_folder]) 
    
    file_name=os.path.join(tmp_folder,str(id_random)+'.txt')
    
    fd=open(file_name,"w")
    fd.write(dump_to_save)
    fd.close()
    
    resp =  static_file(str(id_random)+'.txt',root=tmp_folder,download=True)
    resp.set_cookie('fileDownload','true');
    return resp

@route('/api/v1/av_result', method='GET')
def get_result_from_av():
    file_hash=clean_hash(request.query.file_hash)
    if len(file_hash) != 40:
        response.code = 400
        return jsonize({'message':'Invalid hash format (use sha1)'})
    
    av_result=get_av_result(file_hash)
    if(av_result==None): return jsonize("Can not get analysis")
    
    return jsonize("File processed")

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Host to bind the API server on', default='localhost', action='store', required=False)
    parser.add_argument('-p', '--port', help='Port to bind the API server on', default=8080, action='store', required=False)
    args = parser.parse_args()
    args.port=int(args.port)
    print args
    run(host=args.host, port=args.port, server='gevent')

