from bottle import route
from bottle import request
from bottle import response
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from bson.json_util import dumps
from db_pool import *


@route('/api/v1/av_count', method='GET')
def av_count():
    count = db.av_analysis.count()
    return dumps({"count": count})
