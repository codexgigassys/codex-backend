from bottle import route
from bottle import request
from bottle import static_file
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from MetaControl.MetaController import *
from Utils.Functions import clean_hash
from Utils.Functions import id_generator
from bson.json_util import dumps
from Utils.Functions import call_with_output
import shutil


@route('/api/v1/export', method='POST')
def export_metadata():
    mdc = MetaController()
    hashes = request.forms.dict.get("file_hash[]")
    dump_to_save = ""
    random_id = id_generator()
    tmp_path = "/tmp/meta_export"
    tmp_folder = os.path.join(tmp_path, random_id)
    call_with_output(["mkdir", "-p", tmp_folder])
    for hash in hashes:
        hash = clean_hash(hash.replace('\r', ''))
        res = mdc.read(hash)
        dump = dumps(res, indent=4)
        file_name = os.path.join(tmp_folder, str(hash) + '.txt')
        fd = open(file_name, "w")
        fd.write(dump)
        fd.close()
    zip_path = os.path.join(tmp_path, random_id + '.zip')
    call_with_output(["zip", "-jr", zip_path, tmp_folder])
    resp = static_file(str(random_id) + '.zip', root=tmp_path, download=True)
    resp.set_cookie('fileDownload', 'true')
    shutil.rmtree(tmp_folder)
    os.remove(zip_path)
    return resp
