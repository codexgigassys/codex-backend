# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import pathmagic
from pymongo import MongoClient
import ssdeep
from env import envget


def searchFuzzy(fuzz, limit, thresh):
    client = MongoClient(envget('metadata.host'), envget('metadata.port'))
    db = client[envget('db_metadata_name')]
    coll_meta = db["db_metadata_collection"]

    f1 = coll_meta.find({}, {"file_id": 1, "fuzzy_hash": 1}).limit(limit)
    l = []
    for f in f1:
        l.append(f)

    ret = {}
    for a in l:
        res = -1
        try:
            res = ssdeep.compare(a["fuzzy_hash"], fuzz)
        except InternalError:
            print(str(res) + "------" +
                  str(a["fuzzy_hash"]) + "-----" + str(a["file_id"]))
            continue
        if(res >= thresh):
            ret[a["file_id"]] = res

    return ret


def searchFull(search, limit):
    # print("1")
    client = MongoClient(envget('metadata.host'), envget('metadata.port'))
    # print("2")
    db = client[envget('db_metadata_name')]
    # print("3")
    coll_meta = db["db_metadata_collection"]
    # print("4")
    f1 = coll_meta.find(search).limit(limit)
    # print("5")
    l = []
    for f in f1:
        l.append(f)

    # print("6")
    ret = []
    for a in l:
        ret.append(str(a["file_id"]))
    # print("7")

    return ret
