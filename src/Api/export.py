from bottle import route
from bottle import request
from bottle import static_file
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from Utils.Functions import jsonize
from MetaControl.MetaController import *
from Utils.Functions import clean_hash
from bson.json_util import dumps
from Utils.Functions import id_generator
from Utils.Functions import call_with_output

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
    call_with_output(["mkdir","-p",tmp_folder])

    file_name=os.path.join(tmp_folder,str(id_random)+'.txt')

    fd=open(file_name,"w")
    fd.write(dump_to_save)
    fd.close()

    resp =  static_file(str(id_random)+'.txt',root=tmp_folder,download=True)
    resp.set_cookie('fileDownload','true');
    return resp
