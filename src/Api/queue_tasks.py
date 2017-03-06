from bottle import route
from bottle import request
from bottle import response
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from bson.json_util import dumps
from env import envget
from rq import Queue
from redis import Redis
import re
import datetime
from Utils.ProcessDate import process_date
from Utils.task import count_valid_hashes_in_task


# Returns a json like
# {'queue_tasks': [ {'queue_name': 'task_no_vt',
#                      'tasks': [ 
#                                 {'task_id': 'asdf',
#                                  'date_enqueued': '2017-03.'},
#                                 etc
@route('/api/v1/queue_tasks', method='GET')
def tasks_on_queue():
    tasks_on_queue = []
    for queue_name in ['task_private_vt','task_public_vt','task_no_vt']:
        tasks_on_queue.append({'queue_name': queue_name,
            'tasks': get_tasks_on_queue(queue_name)})

        return dumps({"queue_tasks": tasks_on_queue, "current_date": str(datetime.datetime.now())})

def get_tasks_on_queue(queue_name):
    q=Queue(queue_name,connection=Redis(host=envget('redis.host')))
    jobs = q.jobs
    tasks=[]
    for job in jobs:
        task = {"date_enqueued": str(process_date(job.to_dict().get('enqueued_at')))}
        '''
        to_dict() returns something like this:
        {u'origin': u'task_no_vt', u'status': u'queued', u'description': u"Api.task.generic_task('N7UFZ56FQDITJ34F40TZB50XAWVNW575QGIL4YEC')", u'created_at': '2017-03-03T20:14:47Z', u'enqueued_at': '2017-03-03T20:14:47Z', u'timeout': 31536000, u'data': '\x80\x02(X\x15\x00\x00\x00Api.task.generic_taskq\x01NU(N7UFZ56FQDITJ34F40TZB50XAWVNW575QGIL4YECq\x02\x85q\x03}q\x04tq\x05.'}
        '''
        task_id = re.search('[A-Z0-9]{40}',job.to_dict().get('description'))
        if task_id is None:
            continue
        task['task_id'] = task_id.group(0)
        task['hashes'] = count_valid_hashes_in_task(task['task_id'])
        tasks.append(task)
    return tasks


