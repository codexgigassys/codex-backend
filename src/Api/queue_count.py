from bottle import route
from bottle import request
from bottle import response
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from bson.json_util import dumps
from Utils.Functions import number_of_jobs_on_queue

@route('/api/v1/queue_count', method='GET')
def task_finished():
    count = (number_of_jobs_on_queue('task_private_vt') +
            number_of_jobs_on_queue('task_public_vt') +
            number_of_jobs_on_queue('task_no_vt'))
    return dumps({"count": count})
