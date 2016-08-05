# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from secrets import env
from pymongo import MongoClient
from Utils.Functions import get_file_id
from MetaControl.MetaController import *
from datetime import datetime

class HashAlerter():
    def __init__(self):
        db_collection = "hash_alerts"
        client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
        db=client[env["db_metadata_name"]]
        self.collection=db[db_collection]
        self.mdc=MetaController()

    def newAlert(self,file_hash,email,description):
        already_added = self.collection.find_one({"file_hash": file_hash, "email": email})
        if(already_added is not None):
            return "Already added. "
        if get_file_id(file_hash) is None:
            self.collection.insert_one({"file_hash": file_hash, "email": email, "description": description, "date": datetime.now()})
            return "Added"
        else:
            return "Already on the DB."


