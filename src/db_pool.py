from pymongo import MongoClient
from secrets import *
if 'client' not in globals():
    print "Creating connection pool"
    client=MongoClient(env["metadata"]["host"],env["metadata"]["port"])
    db=client[env["db_metadata_name"]]

