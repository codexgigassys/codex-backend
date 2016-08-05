# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from bottle import route, request
from HashAlerter import *
from Utils.Functions import clean_hash,valid_hash

@route('/api/v1/alerts/new', method='OPTIONS')
def enable_cors_for_alerts_new():
    return 0


@route('/api/v1/alerts/new', method='POST')
def alerts_new():
    hashes = request.forms.dict.get("file_hash[]")
    if hashes is None:
        hashes = request.forms.get("file_hash").split("\n")
    if hashes is None:
        return jsonize({'message':'Error. no file selected'})
    email = request.forms.get("email")
    description = request.forms.get("description")

    ha = HashAlerter()
    resp=""
    for h in hashes:
        cleaned_h = clean_hash(h)
        if(valid_hash(cleaned_h)):
            resp+=str(cleaned_h)+": "+ha.newAlert(cleaned_h,email,description)
        else:
            resp+=str(cleaned_h)+": not a valid hash"
        resp+="\n"

    return resp


