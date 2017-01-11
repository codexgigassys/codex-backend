from redis import Redis
from redis_semaphore import Semaphore
from threading import Thread
import urllib2
import time
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from db_pool import *
from datetime import timedelta
from datetime import datetime

class KeyManager():
    def __init__(self):
        self.semaphore = Semaphore(Redis(host=env.get('redis').get('host')), count=1, namespace='example')

    # When a private key is out of credits
    # we will block it until 00:00 UTC
    def block_key(self,apikey):
        doc = db.vtkeys.find()
        if doc.count()!=1:
            raise ValueError("doc.count() != 1! (check db.vtkeys in DB_Metadata)")
        db.vtkeys.update_one({"doc": 1},{"$set": {apikey+".blocked": True }},upsert=False)

    def reset_daily_counter(self):
        print "reset_daily_counter"
        doc = db.vtkeys.find()
        if doc.count()!=1:
            raise ValueError("doc.count() != 1! (check db.vtkeys in DB_Metadata)")
        doc = doc[0]
        print "doc.keys()="+str(doc.keys())
        for key in doc.keys():
            if key == "doc" or key == "_id":
                continue
            print "key="+str(key)
            db.vtkeys.update_one({"doc": 1},{"$set": {key+".daily": 0}},upsert=False)
            db.vtkeys.update_one({"doc": 1},{"$set": {key+".blocked": False}},upsert=False)
        return True


    # Returns True if there is at least one VirusTotal key in 
    # secrets file.
    def check_keys_in_secrets(self):
        if ((env.get('vt_public_apikey') is None or env.get('vt_public_apikey') == "" ) and
                (env.get('vt_private_apikey') is None or env.get('vt_private_apikey') == "")):
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
                config_str = 'vt_'+p+'_apikey'
                if type(env.get(config_str))==list:
                    keys[p].extend(env.get(config_str))
                elif isinstance(env.get(config_str),basestring):
                    keys[p].append(env.get(config_str))
            return keys


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
        if env.get('debug'): print "get_key()"
        if operation != "av_analysis" and operation != "download_sample":
            raise ValueError("operation invalid")
        if priority is not None and priority != "low" and priority != "high":
            raise ValueError("priority invalid")
        if priority is None:
            priority = "low"
        print "waiting for semaphore"
        keys = self.get_keys_from_secrets()
        if len(keys["public"])==0 and len(keys["private"])==0:
            print "No VT keys"
            return None
        with self.semaphore:
            if env.get('debug'): print "inside semaphore"
            if(db.vtkeys.find().count()==0):
                db.vtkeys.insert({"doc": 1})
            doc = db.vtkeys.find({"doc": 1})
            if doc.count() != 1:
                raise ValueError("doc.count() is different from 1. it did not create a doc in vtkeys collection?")
            doc = doc[0] # get first and only document
            if operation == "av_analysis":
                if env.get('debug'): print "operation == av_analysis"
                timeleft_vec = []
                for key in keys["public"]: # we try to find a public VT api key
                    key_data = doc.get(key)
                    if env.get('debug'): print "key_data="+str(key_data)
                    if key_data is None: # first time a key is used.
                        new_document = { key: { "total": 1, "daily": 1, "blocked": False  }}
                        db.vtkeys.update_one({"doc": 1},{"$set": new_document },upsert=True)
                        db.vtkeys.update_one({"doc": 1},{'$currentDate':{ key+".last_modified": { '$type': "date" } }})
                        return {"key": key}
                    else: # not the first time the key is used.
                        print "key_data="+str(key_data)
                        date_last_used=key_data.get("last_modified")
                        fifteen_sec_ago=(datetime.now()-timedelta(seconds=15))

                        if(key_data.get('blocked') == False and date_last_used < fifteen_sec_ago ):
                            # key is ready to be used
                            if env.get('debug'): print "not blocked"
                            doc_to_update = { key+".total": key_data.get('total')+1,
                                key+".daily": key_data.get('daily')+1}
                            db.vtkeys.update_one({"doc": 1},{"$set": doc_to_update })
                            db.vtkeys.update_one({"doc": 1},{'$currentDate': { key+".last_modified": { '$type': "date" }}})
                            return {"key": key}
                        else: # key is not ready to be used.
                            if key_data.get('blocked')==True:
                                if env.get('debug'): print "public key "+str(key_data.get('key'))+" is blocked."
                                continue
                            if priority == "low":
                                # add timeleft in seconds to arrayj
                                print "a="+str(fifteen_sec_ago)
                                print "b="+str(date_last_used)
                                timeleft_in_seconds = float((date_last_used-fifteen_sec_ago).seconds)+float((date_last_used-fifteen_sec_ago).microseconds)/1000000
                                timeleft_vec.append({"key": key, "timeleft": timeleft_in_seconds })
                                print "timeleft_vec="+str(timeleft_vec)
                if priority == "low": #if priority low, we should ask the worker to wait.
                    print "no public keys available right now"
                    # so we don't spend a credit from the private key.
                    # we should return the smallest timeleft.
                    timeleft_sorted = sorted(timeleft_vec,key=lambda k: k["timeleft"])
                    print "timeleft_sorted="+str(timeleft_sorted)
                    return {"key": None, "timeleft": timeleft_sorted[0].get('timeleft')}

            if operation=="download_sample" or (operation=="av_analysis" and priority=="high"):
            # we should return the private key that has more credits.
                private_keys_vec = []
                for key in keys["private"]:
                    key_data = doc.get(key)
                    if key_data is None: #first time the private key is used
                        new_document = { key: {"total": 1, "daily": 1, "blocked" : False}}
                        db.vtkeys.update_one({"doc": 1},{"$set": new_document})
                        db.vtkeys.update_one({"doc": 1},{"$currentDate": { key+".last_modified": {"$type": "date"} }  })
                        return {"key": key}
                    else:
                        if key_data.get('blocked') == False:
                            private_keys_vec.append({"key": key, "daily": key_data.get('daily')})
                private_keys_sorted = sorted(private_keys_vec,key=lambda k: k["daily"])
                if len(private_keys_sorted)>0:
                    key = private_keys_sorted[0].get('key')
                    db.vtkeys.update_one({"doc": 1},{"$inc": { key+".daily": 1, key+".total": 1 } })
                    db.vtkeys.update_one({"doc": 1},{"$currentDate": { key+".last_modified": {"$type": "date"} }  })
                    return {"key": private_keys_sorted[0].get('key')}
                elif len(keys["private"])!=0: #we have private keys, but they are blocked
                    return {"key": None, "timeleft": 60}
            print str(doc)
        print "left semaphore"
