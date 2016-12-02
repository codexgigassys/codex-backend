# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
import sys
path=os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)
from Utils.Functions import process_file,valid_hash,clean_hash,get_file_id
from PackageControl.PackageController import *

def generic_process_hash(hash_str):
    if hash_str is None:
        return None
    hash_str = clean_hash(hash_str)
    if(not valid_hash(hash_str)):
        return None
    if(len(hash_str) == 64):
        hash_str=get_file_id(hash_str)
    elif(len(hash_str) == 32):
        pc = PackageController()
        hash_str = pc.md5_to_sha1(hash_str)
        print "generic_process_hash-->sha1: "+str(hash_str)
    if(hash_str is not None):
        return process_file(hash_str)
    else :
        return None
