import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from MetaControl.MetaController import *
from Utils.Functions import change_date_to_str
from Utils.Functions import add_error
from Utils.Functions import id_generator
from rq import Queue
from redis import Redis
import datetime

def get_task(task_id):
    mc = MetaController()
    task_report = mc.read_task(task_id)
    if task_report is not None:
        return change_date_to_str(task_report)
    else:
        return add_error({}, 8, "Task not found")

def add_task(process,file_hash,vt_av,vt_samples,email,document_name):
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
    if vt_samples:
        queue_name = "task_private_vt" # task needs a private VT api
    elif vt_av and not vt_samples:
        queue_name = "task_public_vt" # task needs a public VT api
    else:
        queue_name = "task_no_vt" # task doesn't need VT
    q = Queue(queue_name, connection=Redis(host=env.get('redis').get('host')))
    job = q.enqueue('Api.task.generic_task', args=(
        process, file_hash, vt_av, vt_samples, email,task_id,document_name), timeout=31536000)
    return task_id

def add_task_to_download_av_result(file_hash):
    return add_task(True,file_hash,True,False,"","[automatic-request-from-api]")

def save(document):
    mc = MetaController()
    task_id = document["task_id"]
    return mc.write_task(task_id,document)
