# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
from env import envget

if 'client' not in globals():
    print "Creating connection pool..."
    client = MongoClient(envget('metadata.host'), envget('metadata.port'))
    db = client[envget('db_metadata_name')]
    client_fs = MongoClient(envget('files.host'), envget('files.port'))
    db_fs = client_fs[envget('db_files_name')]
    client_ver = MongoClient(envget('versions.host'), envget('versions.port'))
    db_ver = client_ver[envget('db_versions_name')]
    if(envget('temporal_files_db')):
        client_temp = MongoClient(
            envget('temp_files.host'), envget('temp_files.port'))
        db_temp = client_temp[envget('db_temp_files_name')]
