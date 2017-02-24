# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
import math
import traceback
import logging
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import sys
sys.path.insert(0, path)
from db_pool import *
#from IPython import embed
from Utils.ProcessDate import process_date
import datetime

# Saves and reads metadata to/from the db.
class MetaController():

    def __init__(self,db_collection=None):
        if db_collection is None:
            db_collection = env["db_metadata_collection"]
        self.collection=db[db_collection]
        self.import_coll=db.imports_tree
        self.av_coll=db.av_analysis
        self.tasks=db.tasks

    def __delete__(self):
        pass

    def read(self,file_id):
        if file_id is None:
            return None
        f=self.collection.find_one({"file_id":file_id})
        if(f==None): return None

        # Antivirus stuff is in another collection
        av_analysis=self.search_av_analysis(file_id)
        if(av_analysis!=None):
            # we don't want all VT metadata to get displayed.
            f["av_analysis"] = { your_key: av_analysis.get(your_key) for your_key in ["scans","positives","total","scan_date"] }
            #f["av_analysis"]=av_analysis

        return f

    def write(self,file_id,data_dic):
        command={"$set":data_dic}
        try:
            self.collection.update_one({"file_id":file_id},command,upsert=True)
        except:
            logging.exception("MetaController() write(). file_id="+str(file_id)+"\ncommand="+str(command))
            #print(command)
            #err=str(traceback.format_exc())
            #print(err)
            return -1
        return 0

    def writeImportsTree(self,imports):
        command={"$inc":{"count":1}}
        bulk=self.import_coll.initialize_unordered_bulk_op()
        execute_bool=False
        for i in imports:
            dll_name=i["lib"]
            funcs=i["functions"]
            for imp_name in funcs:
                execute_bool=True
                bulk.find({"function_name":imp_name.lower(),"dll_name":dll_name.lower()}).upsert().update(command)
                #print("**** Error Imports Tree ****")
                #err=str(traceback.format_exc())
                #print(err)
                #return -1
        try:
            if(execute_bool):bulk.execute({'w':0})
        except:
            logging.exception("MetaController(): "+str("**** Error Imports Tree ****"))
            #err=str(traceback.format_exc())
            #print(err)
            return -1
        return 0

    def searchImportByName(self,import_name):
        r=self.import_coll.find_one({"function_name":import_name})
        return r

    def searchDllByName(self,dll_name):
        r=self.import_coll.find_one({"dll_name":dll_name})
        return r

    def searchExactImport(self,import_name,dll_name):
        r=self.import_coll.find_one({"function_name":import_name,"dll_name":dll_name})
        return r

    def count_section_used(self,section_sha1):
        f=self.collection.find({"particular_header.sections.sha1":section_sha1}).count()
        return f

    def count_resources_used(self,resources_sha1):
        f=self.collection.find({"particular_header.res_entries.sha1":resources_sha1}).count()
        return f

    def search_av_analysis(self,file_id):
        f=self.av_coll.find_one({"sha1":file_id})
        return f

    def save_first_seen(self,file_id,vt_date):
        if vt_date is None:
            return None
        old_date = self.get_first_date(file_id)
        if old_date is None or vt_date < old_date:
            self.write(file_id,{"date": vt_date})

    def get_first_date(self,file_id):
        meta = self.read(file_id)
        if meta is None:
            return None
        else:
            date = meta.get('date')
            if(type(date)==type(datetime.datetime.now())):
                return date
            else:
                try:
                    date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
                except:
                    date = None
                return date

    def read_task(self,task_id):
        f=self.tasks.find_one({"task_id": task_id})
        return f

    def write_task(self,task_id,data_dic):
        command={"$set":data_dic}
        logging.debug("write_task(): data_dic=")
        logging.debug(str(data_dic))
        return self.tasks.update_one({"task_id": task_id},command,upsert=True)

    def save_av_analysis(self,file_id,analysis_result):
        command={"$set":analysis_result}
        try:
            self.av_coll.update_one({"sha1":file_id},command,upsert=True)
        except:
            logging.exception("**** Error File: %s ****"%(file_id,))
            #print(command)
            #err=str(traceback.format_exc())
            #print(err)
            return -1
        self.save_first_seen(file_id,analysis_result.get('date'))
        return 0

#****************TEST_CODE******************
def testCode():
    pass


#****************TEST_EXECUTE******************
from Utils.test import test
test("-test_MetaController",testCode)
