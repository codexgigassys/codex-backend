# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from pymongo import MongoClient
try:
    from secrets import env
except ImportError:
    from default_config import env
if 'client' not in globals():
    print "Creating connection pool..."
    client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
    db=client[env["db_metadata_name"]]

