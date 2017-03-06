import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from MetaControl.MetaController import *
from Utils.Functions import change_date_to_str
from Utils.Functions import add_error
from Utils.Functions import id_generator
from Utils.Functions import check_hashes
from rq import Queue
from redis import Redis
import datetime

def get_task(task_id):
    task_report = load_task(task_id)
    if task_report is not None:
        return change_date_to_str(task_report)
    else:
        return add_error({}, 8, "Task not found")

def add_task(requested):
    task_id = id_generator(40)
    if requested.get('document_name') is None:
        requested["document_name"]=""

    response = {"requested": requested,
        "date_enqueued": datetime.datetime.now(),
        "task_id": task_id }
    save(response)
    if requested.get('vt_samples'):
        queue_name = "task_private_vt" # task needs a private VT api
    elif requested.get('vt_av') and not requested.get('vt_samples'):
        queue_name = "task_public_vt" # task needs a public VT api
    else:
        queue_name = "task_no_vt" # task doesn't need VT
    q = Queue(queue_name, connection=Redis(host=envget('redis.host')))
    job = q.enqueue('Api.task.generic_task', args=(task_id,), timeout=31536000)
    return task_id

def add_task_to_download_av_result(file_hash):
    requested = {'process': True,
            'file_hash': file_hash,
            'vt_av': vt_av,
            'vt_samples': False,
            'email': '',
            'document_name': '[automatic-request-from-api]',
            'ip': '127.0.0.1'}
    return add_task(requested)

def save(document):
    mc = MetaController()
    task_id = document["task_id"]
    return mc.write_task(task_id,document)

def load_task(task_id):
    mc = MetaController()
    return mc.read_task(task_id)

def count_valid_hashes_in_task(task_id):
    task = get_task(task_id)
    file_hash = task.get('requested',{}).get('file_hash')
    if file_hash is None:
       return 0
    output = check_hashes(file_hash)
    if output.get('hashes') is None:
        return 0
    return len(output.get('hashes'))
