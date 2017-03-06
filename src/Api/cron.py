import pathmagic
from bottle import route, request, response
from Utils.Functions import jsonize, change_date_to_str
from PackageControl.PackageController import *
from KeyManager.KeyManager import *

# Resets the daily counters
# of the private keys


@route('/api/v1/cron', method='GET')
def cron():
    key_manager = KeyManager()
    key_manager.reset_daily_counter()
    return jsonize({"status": "ok"})
