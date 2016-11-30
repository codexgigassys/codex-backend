from bottle import route
from bottle import request
from bottle import response
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from Utils.Functions import jsonize
from bson.json_util import dumps
from Utils.Functions import clean_hash
from Utils.Functions import check_hashes
from Utils.Functions import change_date_to_str
from Utils.Functions import id_generator
from Utils.Functions import to_bool
from Utils.Functions import get_file_id
from Utils.Functions import add_error
from PackageControl.PackageController import *
from MetaControl.MetaController import *
from process_hash import generic_process_hash
from virusTotalApi import get_av_result
from virusTotalApi import save_file_from_vt
from Utils.mailSender import send_mail
import datetime
from rq import Queue
from redis import Redis
from IPython import embed

@route('/api/v1/task', method='OPTIONS')
def enable_cors_for_task():
    return 0

# Return true if the task has
# finished. False otherwise.
@route('/api/v1/task_finished', method='GET')
def task_finished():
    task_id = request.query.get('task_id')
    task = get_task(task_id)
    return dumps({"has_finished": task.get('date_end') is not None})

@route('/api/v1/task', method='GET')
def api_get_task():
    task_id = request.query.get('task_id')
    return dumps(get_task(task_id))

def get_task(task_id):
    mc = MetaController()
    task_report = mc.read_task(task_id)
    if task_report is not None:
        return change_date_to_str(task_report)
    else:
        return add_error({}, 8, "Task not found")

@route('/api/v1/task', method='POST')
def task():
    file_hash = request.forms.get('file_hash')
    vt_av = to_bool(request.forms.get('vt_av'))
    vt_samples = to_bool(request.forms.get('vt_samples'))
    process = to_bool(request.forms.get('process'))
    email = request.forms.get('email')
    document_name = request.forms.get('document_name')

    task_id = id_generator(40)
    response = {"requested": {
        "vt_av": vt_av,
        "vt_samples": vt_samples,
        "process": process,
        "email": email,
        "document_name": document_name,
        "file_hash": file_hash
        },
        "date_enqueued": datetime.datetime.now(),
        "task_id": task_id }
    save(response)
    q = Queue('task', connection=Redis())
    job = q.enqueue('Api.task.generic_task', args=(
        process, file_hash, vt_av, vt_samples, email,task_id,document_name), timeout=31536000)
    return dumps({"task_id": task_id})


def generic_task(process, file_hash, vt_av, vt_samples, email,task_id,document_name=""):
    response = {}
    response["date_start"] = datetime.datetime.now()
    response["document_name"] = document_name
    response["task_id"] = task_id
    check_hashes_output = check_hashes(file_hash)
    errors = check_hashes_output.get('errors')
    for key,value in errors:
        response = add_error(response, key, value)
    hashes = check_hashes_output.get('hashes')
    response["hashes"] = hashes
    if(len(hashes) == 0):
        response = add_error(response, 6, "No valid hashes provided.")
        return change_date_to_str(response)

    response["not_found"] = []
    if vt_samples:
        response["downloaded"] = []
        for hash_id in hashes:
            if(get_file_id(hash_id) is None):
                if(save_file_from_vt(hash_id) is not None):
                    response["downloaded"].append(hash_id)
                    generic_process_hash(hash_id)
                else:
                    response["not_found"].append(hash_id)
    save(response)
    response["processed"] = []
    if process:
        for hash_id in hashes:
            process_start_time = datetime.datetime.now()
            if(generic_process_hash(hash_id) == 0):
                process_end_time = datetime.datetime.now()
                response["processed"].append({"hash": hash_id,
                    "seconds": (process_end_time-process_start_time).seconds})
            else:
                response["not_found"].append(hash_id)
    response["not_found"] = list(set(response["not_found"]))
    save(response)
    if vt_av:
        for hash_id in hashes:
            sha1 = get_file_id(hash_id)
            if(sha1 is not None):
                get_av_result(sha1)

    if(bool(email)):
        send_mail(email, "task done", str(response))
    response["date_end"] = datetime.datetime.now()
    save(response)
    return response

def save(document):
    mc = MetaController()
    task_id = document["task_id"]
    return mc.write_task(task_id,document)
