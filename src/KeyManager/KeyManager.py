import pathmagic
from redis import Redis
from redis_semaphore import Semaphore
from threading import Thread
import urllib2
import time
from db_pool import *
import datetime
import logging


class KeyManager():

    def __init__(self):
        self.semaphore = Semaphore(
            Redis(host=envget('redis.host')), count=1, namespace='example')

    def log_daily_key_use(self):
        logging.debug("KeyManager(): log_key_use")
        doc = db.vtkeys.find()
        if doc.count() != 1:
            raise ValueError(
                "doc.count() != 1! (check db.vtkeys in DB_Metadata)")
        doc = doc[0]
        date = datetime.datetime.now()
        doc["date"] = date
        doc.pop('_id', None)
        db.logs.insert_one(doc)

    def log_operation_result(self, key, operation, result):
        db.vtkeys.update_one({"doc": 1}, {"$inc": {key + "." + operation + ".daily." + result: 1,
                                                   key + "." + operation + ".total." + result: 1}})

    # When a private key is out of credits
    # we will block it until 00:00 UTC
    def block_key(self, apikey):
        doc = db.vtkeys.find()
        if doc.count() != 1:
            raise ValueError(
                "doc.count() != 1! (check db.vtkeys in DB_Metadata)")
        date = datetime.datetime.now()
        db.vtkeys.update_one(
            {"doc": 1}, {"$set": {apikey + ".blocked": True}}, upsert=False)
        db.vtkeys.update_one(
            {"doc": 1}, {"$set": {apikey + ".blocked_time": date}}, upsert=False)

    def reset_daily_counter(self):
        logging.debug("KeyManager(): reset_daily_counter")
        logging.debug("KeyManager(): log_key_use")
        self.log_daily_key_use()
        logging.debug("KeyManager():</log_key_use>")
        doc = db.vtkeys.find()
        if doc.count() != 1:
            raise ValueError(
                "doc.count() != 1! (check db.vtkeys in DB_Metadata)")
        doc = doc[0]
        logging.debug("KeyManager(): doc.keys()=" + str(doc.keys()))
        for key in doc.keys():
            if key == "doc" or key == "_id":
                continue
            logging.debug("KeyManager(): key=" + str(key))
            db.vtkeys.update_one(
                {"doc": 1}, {"$set": {key + ".daily": 0}}, upsert=False)
            db.vtkeys.update_one(
                {"doc": 1}, {"$set": {key + ".download_sample.daily": {}}}, upsert=False)
            db.vtkeys.update_one(
                {"doc": 1}, {"$set": {key + ".av_analysis.daily": {}}}, upsert=False)
            db.vtkeys.update_one(
                {"doc": 1}, {"$set": {key + ".blocked": False}}, upsert=False)
        return True

    def check_private_key(self):
        keys = self.get_keys_from_secrets()
        if len(keys.get('private')) == 0:
            return False
        for private_key in keys.get('private'):
            if not self.is_key_blocked(private_key):
                return True
        return False

    def is_key_blocked(self, key_str):
        doc = db.vtkeys.find({"doc": 1, key_str + ".blocked": True})
        if doc.count() == 0:
            return False
        else:
            return True

    # Returns True if there is at least one VirusTotal key in
    # secrets file.
    def check_keys_in_secrets(self):
        if ((envget('vt_public_apikey') is None or envget('vt_public_apikey') == "") and
                (envget('vt_private_apikey') is None or envget('vt_private_apikey') == "")):
            return False
        else:
            return True

    def get_keys_from_secrets(self):
        if not self.check_keys_in_secrets():
            return {"public": [], "private": []}
        else:
            keys = {}
            for p in ["public", "private"]:
                keys[p] = []
                config_str = 'vt_' + p + '_apikey'
                if type(envget(config_str)) == list:
                    keys[p].extend(envget(config_str))
                elif isinstance(envget(config_str), basestring):
                    keys[p].append(envget(config_str))
            return keys

    def init_key_in_document(self, key):
        new_document = {key: {"total": 1, "daily": 1,
                              "download_sample": {}, "av_analysis": {}, "blocked": False}}
        db.vtkeys.update_one({"doc": 1}, {"$set": new_document}, upsert=True)
        db.vtkeys.update_one({"doc": 1}, {'$currentDate': {
                             key + ".last_modified": {'$type': "date"}}})

    def add_one_to_key(self, key):
        db.vtkeys.update_one(
            {"doc": 1}, {"$inc": {key + ".daily": 1, key + ".total": 1}})
        db.vtkeys.update_one({"doc": 1}, {"$currentDate": {
                             key + ".last_modified": {"$type": "date"}}})

    # get_key returns the key that optimize the use
    # of credits. There are only two valid operations:
    # 'av_analysis' and 'download_sample'. 'av_analysis'
    # operation is to download the Antivirus scans
    # for a specific sample. It can be donde  with
    # VirusTotal public API. While 'download_sample'
    # needs a private VirusTotal API key.
    # If operation is av_analysis, a public key will
    # be used if possible. If there are not public keys
    # available for use at the moment (there is an anti-flood
    # protection of 15 seconds) one of two things can happen.
    # if the priority is low, it will return a dictionary like this:
    # { 'key': None, 'timeleft': 5 seconds}, where 5 seconds is the minimun
    # time the worker needs to wait to ask again for a key.
    # If the priority is high, it will return a private key.
    # (It chooses the private key that has less credits spent in the day
    def get_key(self, operation, priority=None):
        logging.debug("KeyManager(): get_key()")
        if operation != "av_analysis" and operation != "download_sample":
            raise ValueError("operation invalid")
        if priority is not None and priority != "low" and priority != "high":
            raise ValueError("priority invalid")
        if priority is None:
            priority = "low"
        logging.debug("KeyManager(): waiting for semaphore")
        keys = self.get_keys_from_secrets()
        if len(keys["public"]) == 0 and len(keys["private"]) == 0:
            logging.info("KeyManager(): No VT keys")
            return None
        with self.semaphore:
            logging.debug("KeyManager(): inside semaphore")
            if(db.vtkeys.find().count() == 0):
                db.vtkeys.insert({"doc": 1})
            doc = db.vtkeys.find({"doc": 1})
            if doc.count() != 1:
                raise ValueError(
                    "doc.count() is different from 1. it did not create a doc in vtkeys collection?")
            doc = doc[0]  # get first and only document
            if operation == "av_analysis":
                logging.debug("operation == av_analysis")
                timeleft_vec = []
                for key in keys["public"]:  # we try to find a public VT api key
                    key_data = doc.get(key)
                    logging.debug("key_data=" + str(key_data))
                    if key_data is None:  # first time a key is used.
                        init_key_in_document(key)
                        return {"key": key}
                    else:  # not the first time the key is used.
                        logging.debug("key_data=" + str(key_data))
                        date_last_used = key_data.get("last_modified")
                        fifteen_sec_ago = (
                            datetime.datetime.now() - datetime.timedelta(seconds=15))

                        if(key_data.get('blocked') is False and date_last_used < fifteen_sec_ago):
                            # key is ready to be used
                            logging.debug("not blocked")
                            self.add_one_to_key(key)
                            return {"key": key}
                        else:  # key is not ready to be used.
                            if key_data.get('blocked') is True:
                                logging.info(
                                    "KeyManager(): public key " + str(key_data.get('key')) + " is blocked.")
                                continue
                            if priority == "low":
                                # add timeleft in seconds to arrayj
                                logging.debug(
                                    "KeyManager(): a=" + str(fifteen_sec_ago))
                                logging.debug(
                                    "KeyManager(): b=" + str(date_last_used))
                                timeleft_in_seconds = float((date_last_used - fifteen_sec_ago).seconds) + float(
                                    (date_last_used - fifteen_sec_ago).microseconds) / 1000000
                                timeleft_vec.append(
                                    {"key": key, "timeleft": timeleft_in_seconds})
                                logging.debug(
                                    "KeyManager(): timeleft_vec=" + str(timeleft_vec))
                if priority == "low":  # if priority low, we should ask the worker to wait.
                    logging.info(
                        "KeyManager(): no public keys available right now")
                    # so we don't spend a credit from the private key.
                    # we should return the smallest timeleft.
                    timeleft_sorted = sorted(
                        timeleft_vec, key=lambda k: k["timeleft"])
                    logging.debug("timeleft_sorted=" + str(timeleft_sorted))
                    return {"key": None, "timeleft": timeleft_sorted[0].get('timeleft')}

            if operation == "download_sample" or (operation == "av_analysis" and priority == "high"):
                # we should return the private key that has more credits.
                private_keys_vec = []
                for key in keys["private"]:
                    key_data = doc.get(key)
                    if key_data is None:  # first time the private key is used
                        init_key_in_document(key)
                        return {"key": key}
                    else:
                        if key_data.get('blocked') is False:
                            private_keys_vec.append(
                                {"key": key, "daily": key_data.get('daily')})
                private_keys_sorted = sorted(
                    private_keys_vec, key=lambda k: k["daily"])
                if len(private_keys_sorted) > 0:
                    key = private_keys_sorted[0].get('key')
                    self.add_one_to_key(key)
                    return {"key": private_keys_sorted[0].get('key')}
                elif len(keys["private"]) != 0:  # we have private keys, but they are blocked
                    return {"key": None, "timeleft": 60}
            logging.debug(str(doc))
        logging.debug("left semaphore")
