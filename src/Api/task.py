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
from Utils.Functions import valid_hash
from PackageControl.PackageController import *
from MetaControl.MetaController import *
from VersionControl.VersionController import *
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
    if vt_av or vt_samples:
        queue_name = "task"
    else:
        queue_name = "task_no_vt"
    q = Queue(queue_name, connection=Redis(host=env.get('redis').get('host')))
    job = q.enqueue('Api.task.generic_task', args=(
        process, file_hash, vt_av, vt_samples, email,task_id,document_name), timeout=31536000)
    return dumps({"task_id": task_id})


def generic_task(process, file_hash, vt_av, vt_samples, email,task_id,document_name=""):
    print "task_id="+str(task_id)
    generic_count = 0
    response = {}
    response["date_start"] = datetime.datetime.now()
    response["document_name"] = document_name
    response["task_id"] = task_id
    check_hashes_output = check_hashes(file_hash)
    errors = check_hashes_output.get('errors')
    for error in errors:
        key = error.get('error')
        value = error.get('error_message')
        print "errors (key="+str(key)+", value="+str(value)+")"
        response = add_error(response, key, value)
    hashes = check_hashes_output.get('hashes')
    remove_dups_output = remove_dups(hashes)
    # remove duplicated hashes
    hashes = remove_dups_output.get('list')
    response["duplicated_hashes"] = remove_dups_output.get('dups')
    response["hashes"] = hashes

    hash_dicts = []
    mc = MetaController()
    for x in hashes:
        x_dict = {}
        x_dict["original"] = x
        x_dict["sha1"] = get_file_id(x)
        if(x_dict["sha1"] is not None):
            doc = mc.read(x_dict["sha1"])
            if doc is not None and doc.get('hash') is not None:
                if doc.get('hash').get('md5') is not None:
                    x_dict["md5"] = doc.get('hash').get('md5')
                if doc.get('hash').get('sha2') is not None:
                    x_dict["sha2"] = doc.get('hash').get('sha2')
        hash_dicts.append(x_dict)
    response["duplicated_samples"] = []
    for x in hash_dicts:
        for y in hash_dicts:
            if x.get('original') != y.get('original') and (
                    x.get('original') == y.get('sha1') or
                    x.get('original') == y.get('md5') or
                    x.get('original') == y.get('sha2')):
                response["duplicated_samples"].append(y.get('original'))
                hash_dicts.remove(y)
    hashes=[]
    for x in hash_dicts:
        hashes.append(x.get('original'))
    response["hashes"]=hashes

    if(len(hashes) == 0):
        response = add_error(response, 6, "No valid hashes provided.")
        response["date_end"] = datetime.datetime.now()
        save(response)
        return change_date_to_str(response)

    save(response)

    response["inconsistencies"]=[]
    for hash_id in hashes:
        if fix_inconsistency(hash_id) == 1:
            response["inconsistencies"].append(hash_id)

    save(response)

    response["not_found_on_vt"] = []
    if vt_samples:
        response["downloaded"] = []
        for hash_id in hashes:
            if(get_file_id(hash_id) is None or db_inconsistency(hash_id)):
                print "task(): "+hash_id+" was not found (get_file_id returned None). "
                generic_count += 1
                if (generic_count % 20 == 0):
                    save(response)
                if(save_file_from_vt(hash_id) is not None):
                    response["downloaded"].append(hash_id)
                    generic_process_hash(hash_id)
                else:
                    response["not_found_on_vt"].append(hash_id)
    save(response)
    response["processed"] = []
    response["not_found_for_processing"] = []
    if process:
        print "process=true"
        for hash_id in hashes:
            print "task: hash_id="+str(hash_id)
            process_start_time = datetime.datetime.now()
            generic_count += 1
            if (generic_count % 20 == 0):
                save(response)
            if(generic_process_hash(hash_id) == 0):
                process_end_time = datetime.datetime.now()
                response["processed"].append({"hash": hash_id,
                    "seconds": (process_end_time-process_start_time).seconds})
            else:
                response["not_found_for_processing"].append(hash_id)
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

# Fix db inconsistencies
# This can happen in old setups
def fix_inconsistency(file_hash):
    status = db_inconsistency(file_hash)
    if status==1 or status==3:
        generic_process_hash(file_hash)
        return 1
    elif status==2:
        file_id = get_file_id(file_hash)
        save_file_from_vt(file_id)
        return 1
    else:
        return 0


# The DB is consistent if the
# file has sample, meta and version,
# or nothing. Is inconsistent otherwise.
# returns 0 if everything is ok
# returns 1 if hash has sample, but not meta
# returns 2 if hash has meta, but not sample
# returns 3 if hash has meta and sample, but not version
def db_inconsistency(file_hash):
    if(not valid_hash(file_hash)):
        raise ValueError("db_inconsistency invalid hash")
    pc = PackageController()
    v = VersionController()
    file_id = get_file_id(file_hash)
    if file_id is not None: #meta exists
        file_bin = pc.getFile(file_id)
        if file_bin is not None: #sample exists
            version = v.searchVersion(file_id)
            if version is not None:
                return 0 # ok
            else: #version does not exist
                return 3
        else: # has meta but not sample
            return 2
    else: # does not have meta
        if len(file_hash)==64:
            return 0 # cant search in grid by sha256
        if len(file_hash)==40:
            file_bin = pc.getFile(file_hash)
        else: # md5
            sha1 = pc.md5_to_sha1(file_hash)
            if sha1 is None:
                return 0 # does not have meta or sample
            file_bin = pc.getFile(file_hash)
        if file_bin is None:
             return 1
        else:
             return 0

def save(document):
    mc = MetaController()
    task_id = document["task_id"]
    return mc.write_task(task_id,document)

def remove_dups(biglist):
    known_links = set()
    newlist = []
    dups = []

    for d in biglist:
        link = d
        if link in known_links:
            dups.append(link)
            continue
        newlist.append(d)
        known_links.add(link)
    biglist[:] = newlist
    return {'list': biglist,'dups': dups}
