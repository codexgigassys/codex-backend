# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import hashlib
import magic
import ssdeep
import logging

def MIME_TYPE(data,mime=True):
    try:
        return magic.from_buffer(data,mime=mime)
    except magic.MagicException:
        return "none/none"

def SHA1(data):
    return hashlib.sha1(data).hexdigest()

def SHA256(data):
    return hashlib.sha256(data).hexdigest()

def MD5(data):
    return hashlib.md5(data).hexdigest()

def getSsdeep(data):
    try:
        res=ssdeep.hash(data)
        return res
    except Exception, e:
        logging.exception(str(e))
        return ''

#****************TEST_CODE******************

def testCode():
    file="../Test_files/test.exe"
    data=(open(file,'rb').read())
    inf=InfoExtractor(data)
    print("Type:      "+str(inf.type()))
    print("MIME_TYPE: "+str(inf.MIME_TYPE()))
    print("SHA1:      "+str(inf.SHA1()))
    print("SHA256:    "+str(inf.SHA256()))
    print("MD5:       "+str(inf.MD5()))
    print("Size:      "+str(inf.size()))
    print("Info:      "+str(inf.MIME_TYPE(False)))

#****************TEST_EXECUTE******************
from test import test
test("-test_InfoExtractor",testCode)
