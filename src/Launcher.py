# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
#Funciones para realizar los analisis

import os
import time
from czipfile import ZipFile
from Cataloger import Cataloger
from Processors.ProcessorFactory import *
from PackageControl.PackageController import *
from VersionControl.VersionController import *
from MetaControl.MetaController import *
from Utils.TimeLogger import TimeLogger
from Sample import *
import logging
try:
    from config.secrets import env
except ImportError:
    from config.default_config import env

class Launcher():

    def __init__(self):
        formato='[%(asctime)-15s][%(levelname)s] %(message)s'
        path=os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        logfile=os.path.join(path,"launcher.log")
        logging.basicConfig(format=formato,filename=logfile, level=logging.INFO)

        self.vc=VersionController()
        self.pc=PackageController()
        self.mdc=MetaController()

        def launchOnlyHashingByID(self,sample):
            sample.setPackageController(self.pc)
            sample.setMetaController(self.mdc)
            sample.setVersionController(self.vc)
            category=sample.getCategory()
            if(category==None):
                category=Cataloger().catalog(sample.getBinary())
                logging.debug("Category not found in DB, categorized as %s",str(category))
            else:
                logging.debug("Category found in DB, categorized as %s",str(category))
            processor=ProcessorFactory().getHashProcessor(category,sample)
            result_dic=processor.process()
            result_version=processor.getVersion()

            if(len(result_version)>0):
                logging.debug("Updating metadata")

                if(self.mdc.write(sample.getID(),result_dic)!=0):
                    logging.error("Error writing Metadata to DB, sample:%s",sample.getID())
                    return -1
                logging.debug("Metadata writed in DB")

                self.vc.updateVersion(sample.getID(),result_version)
                logging.debug("Versions writed to DB")
            else:

                logging.debug("Nothing to update")

            logging.debug("Analysis Finished OK")
            return 0

    def launchAnalysisByID(self,sample):
        logging.debug("Launching Analysis on sample:%s",sample.getID())
        sample.setPackageController(self.pc)
        sample.setMetaController(self.mdc)
        sample.setVersionController(self.vc)

        category=sample.getCategory()
        if(category==None):
            category=Cataloger().catalog(sample.getBinary())
            logging.debug("Category not found in DB, categorized as %s",str(category))
        else:
            logging.debug("Category found in DB, categorized as %s",str(category))

        processor=ProcessorFactory().createProcessor(category,sample)
        result_dic=processor.process()
        result_version=processor.getVersion()

        if(len(result_version)>0):
            logging.debug("Updating metadata")

            if(self.mdc.write(sample.getID(),result_dic)!=0):
                logging.error("Error writing Metadata to DB, sample:%s",sample.getID())
                return -1
            logging.debug("Metadata writed in DB")

            self.vc.updateVersion(sample.getID(),result_version)
            logging.debug("Versions writed to DB")
        else:

            logging.debug("Nothing to update")

        logging.debug("Analysis Finished OK")
        return 0


#****************TEST_CODE******************
from pymongo import MongoClient
import gridfs
from Utils.test import test
import time

def testCode():
    from Utils.Functions import recursive_read
    object="./Test_files/"
    files=recursive_read(object)
    if(files==None): sys.exit()
    lc=Launcher()
    for fp in files:
        fd=open(fp,'r')
        data=fd.read()
        file_id=hashlib.sha1(data).hexdigest()
        print("%s %s"%(fp,file_id))
        lc.launchFileAnalitics((fp,data))
        print("")
    print("")

#-----------------------------------------------
def testCode2():
    object="../processed/VirusShare_00000.zip"
    # opening zipped package
    fd=open(object,'r')
    zf= ZipFile(fd)
    names=zf.namelist() # name of compressed files

    lc=Launcher()
    count=0
    reset=0
    for filename in names:
        #print(filename)
        data=zf.read(filename,"infected")
        lc.launchFileAnalitics((filename,data))
        reset+=1
        count+=1
        if(reset>=1000):
            print(str(count)+" processed")
            reset=0
    print(str(count)+" processed")

#----------------------------------------------
def testCode3():
    object="../DB/packages/fileindex"
    # opening the index
    fd=open(object,'r')
    lc=Launcher()
    count=0
    reset=0
    while True:
        #start=time.time()
        rl=fd.readline()
        if(rl==""):break
        data=rl.strip().split('|')
        #print(data)
        fd2=open("../DB/packages/"+str(data[1])+"/p"+str(data[2])+".index")
        fd2.seek(int(data[3]))
        rl2=fd2.readline()
        data1=rl2.strip().split('|')
        #print(data1)
        fd3=open("../DB/packages/"+str(data[1])+"/p"+str(data[2])+".paq")
        fd3.seek(int(data1[1]))
        datafin=fd3.read(int(data1[2]))
        #end=time.time()
        #print("search :"+str((end-start)*10000))
        #start=time.time()
        lc.launchFileAnalitics((data[0],datafin))
        #end=time.time()
        #print("analize :"+str((end-start)*10000))
        #print("")
        reset+=1
        count+=1
        if(reset>=1000):
            print(str(count)+" processed")
            reset=0

    print(str(count)+" processed")

#----------------------------------------------
def testCode4():
    inicio=10569000
    client=MongoClient(env["files"]["host"],env["files"]["port"])
    db=client[env["db_files_name"]]
    fs=gridfs.GridFS(db)
    res=fs.find(timeout=False).skip(inicio)
    lc=Launcher()
    count=inicio; reset=0
    for f in res:
        data=f.read()
        #print(f.filename,count)
        lc.launchFileAnalitics((f.filename,data))
        reset+=1; count+=1
        if(reset>=1000):
            print(str(count)+" processed")
            reset=0
    print(str(count)+" processed")

#----------------------------------------------
def testCode5():
    lc=Launcher()
    sample=Sample()
    sample.setID("0358ab4e8595db846b709cf85d7b397d92230bef")
    #sample.setID("223e8761fbb93458140a3592096109501927ff64")
    sample.setStorageVersion({})
    lc.launchAnalysisByID(sample)
    #print(sample.getCalculatedMetadata().getData())
    #print(sample.getCalculatedVersion())
    #print(sample.getStorageVersion())

#----------------------------------------------
def testCode6():
    inicio=0
    client=MongoClient(env["files"]["host"],env["files"]["port"])
    db=client[env["db_files_name"]]
    fs=gridfs.GridFS(db)
    res=fs.find(timeout=False).skip(inicio)
    lc=Launcher()
    count=inicio; reset=0
    start=time.time()
    first=True
    for f in res:
        sam_id=f.filename
        sample=Sample()
        sample.setID(sam_id)
        sample.setStorageVersion({})
        lc.launchAnalysisByID(sample)
        reset+=1; count+=1
        if(reset>=1000):
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+" processed:"+str(count/1000)+"K")
            reset=0
    print(str(count)+" processed")


#****************TEST_EXECUTE******************
test("-test_Launcher",testCode6)



