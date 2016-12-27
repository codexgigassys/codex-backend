# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
try:
    from config.secrets import env
except ImportError:
    from config.default_config import env
if 'client' not in globals():
    print "Creating connection pool..."
    client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
    db=client[env["db_metadata_name"]]
    client_fs=MongoClient(env["files"]["host"],env["files"]["port"])
    db_fs=client_fs[env["db_files_name"]]
    client_ver=MongoClient(env["versions"]["host"],env["versions"]["port"])
    db_ver=client_ver[env["db_versions_name"]]
    if(env["temporal_files_db"]):
        client_temp=MongoClient(env["temp_files"]["host"],env["temp_files"]["port"])
        db_temp=client_temp[env["db_temp_files_name"]]

