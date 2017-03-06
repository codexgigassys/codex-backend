from bottle import route, request, response
from Utils.Functions import jsonize, change_date_to_str
import os
path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
import sys
sys.path.insert(0, path)
from PackageControl.PackageController import *
from KeyManager.KeyManager import *

# Resets the daily counters
# of the private keys


@route('/api/v1/cron', method='GET')
def cron():
    key_manager = KeyManager()
    key_manager.reset_daily_counter()
    return jsonize({"status": "ok"})
