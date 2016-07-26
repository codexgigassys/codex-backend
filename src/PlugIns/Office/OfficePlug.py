# Microsoft Office metadata and macro extracter plugin
# This plugin needs: 
# * python-hachoir-metadata (apt-get install python-hachoir-metadata)
# * read and write access to /tmp
from PlugIns.PlugIn import PlugIn
from subprocess import call
import os
from Utils.InfoExtractor import *
import os
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','PackageControl'))
import sys
sys.path.insert(0, path)
from PackageControl.PackageController import *
import subprocess
import re
import datetime

def is_float(f):
    try:
        float(f)
        return True
    except ValueError:
        return False

def get_hash(algorithm,path_to_file):
    if algorithm not in ["md5","sha1","sha256"]:
        return None
    output=call_with_output([algorithm+"sum",path_to_file])
    return output.split()[0]
    
def get_basic_stuff_from_file(path_to_file,filename):
    dic={}
    dic["filename"]=filename
    dic["md5"]=get_hash("md5",path_to_file)
    dic["sha1"]=get_hash("sha1",path_to_file)
    dic["sha256"]=get_hash("sha256",path_to_file)
    dic["size"]=os.path.getsize(path_to_file)
    return dic


def call_with_output(array):
    p = subprocess.Popen(array, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err = p.communicate()
    return output

def save_in_hash(office_hash,subindex,meta,value):
    if subindex == None or subindex == None or meta == None or value == None or (not value.isdigit() and len(value)==0):
        return office_hash
    
    if value.isdigit():
        value=int(value)
    elif is_float(value):
        value=float(value)

    if subindex=="common":
        if meta in ['creation_date','last_modification','endian','nb_page','producer','file_size','filename','compr_size','compression','compr_rate','mime_type']:
            office_hash[subindex][meta]=value
        else:
            if office_hash[subindex].get(meta) is None:
                office_hash[subindex][meta]=[]
            office_hash[subindex][meta].append(value)
    elif isinstance(subindex,int):
        office_hash["file"][subindex][meta]=value
    return office_hash


class OfficePlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)
        self.pc = PackageController('localhost',29017,'DB_macros')
        
    def getPath(self):
        return "office"
                
    def getName(self):
        return "office"
    
    def getVersion(self):
        return 1
            
    def process(self):
        #process use three tools:
        # hachoir-metadata
        # office_parser
        # 7zip
        if self.sample is None:
            return []
        #create a folder for extracting macros 
        folder_path = os.path.join("/tmp/codex/officeplug/",self.sample.getID())
        macro_folder_path = os.path.join(folder_path,"macros")
        call(["rm","-r",folder_path]) 
        p7z="/usr/bin/7z"
        call(["mkdir","-p",folder_path]) 
        call(["mkdir","-p",macro_folder_path]) 
        file_path=os.path.join(folder_path,self.sample.getID())+".codex"
        file_p = open(file_path,"wb")
        bytearray_data = bytearray(self.sample.getBinary())
        file_p.write(bytearray_data)
        file_p.close()
        office_parser_path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"officeparser.py"))
        # extract metadata with hachoir-metadata
        p = subprocess.Popen(['hachoir-metadata','--raw',"--level=9","--quality=1.0",file_path], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
        office_metadata,err = p.communicate()
        office_meta_hash={}
        #clean hachoir-metadata output
        files=[]
        subindex="common"
        office_meta_hash["common"]={}
        for i in office_metadata.splitlines():
            if i == "Common:" or i=="Metadata:":
                subindex = "common"
            elif re.search("file\[[0-9]+\]",i) != None:
                subindex=int(re.search("[0-9]+",i).group(0))
                if office_meta_hash.get("file") is None:
                    office_meta_hash["file"]=[]
                office_meta_hash["file"].append({})
                #if len(tmp_file)
                tmp_file={}
            else:
                meta_value_array =  i[2:].split(":",1) #each line has the format variable: value
                if meta_value_array[1][-2:] == '\\0':
                    #remove explicit \0 (\\0) at the end.
                    meta_value_array[1]=meta_value_array[1][:-2]

                #remove whitespaces at the beginning and end
                meta_value_array[1]=meta_value_array[1].strip()
                office_meta_hash=save_in_hash(office_meta_hash,subindex,meta_value_array[0],meta_value_array[1])
        office_meta_hash["macros"]=[]
        ##### office_parser.py : works for old .doc not for docx apprently #####
        # sometimes it crash inside office_parser.py, but because we execute it as an external call,
        # it is not a problem
        # office_parser.py from here: https://github.com/unixfreak0036/officeparser
        call(["python",office_parser_path,"--extract-macros",file_path,"-o",macro_folder_path])
        dic=[]
        for macro in os.listdir(macro_folder_path):
            macro_metadata={}
            try:
                data = open(os.path.join(macro_folder_path,macro),"rb").read()
            except:
                continue
            macro_metadata["sha1"]=SHA1(data)
            macro_metadata["md5"]=MD5(data)
            macro_metadata["size"]=len(data)
            macro_metadata["name"]=str(macro)
            macro_metadata["sha2"]=SHA256(data)
            macro_metadata["fuzzy"]=getSsdeep(data)
            dic.append(macro_metadata)
            #call(["rm",os.path.join(folder_path,macro)])

            if self.pc.getFile(macro_metadata["sha1"])==None:
                self.pc.append(macro_metadata["sha1"],data)
        office_meta_hash["macros"]=dic
        # extract via 7z 
        p7z_output=os.path.join(folder_path,"7z")
        call(["mkdir","-p",p7z_output])
        call([p7z,"x",file_path,"-o"+p7z_output])
        for command in ["md5sum","sha256sum","sha1sum"]:
            p = subprocess.Popen(["find",p7z_output,"-type","f","-exec",command,"{}",";"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            find_output,err=p.communicate()
            for i in find_output.splitlines():
                file_hash_array = i.split(" ",1) #each line has the format "file hash"
                hash=file_hash_array[0]
                filename=file_hash_array[1].replace(p7z_output+"/","").strip()
                #search for that file in office_meta_hash["file"]
                found=False
                if office_meta_hash.get("file") is not None:
                    for file_in_hash in office_meta_hash.get("file"):
                        if filename == file_in_hash.get("filename"):
                            file_in_hash[command.replace('sum','')]=hash
                            found=True
                            break
                    if not found:
                        new_file = get_basic_stuff_from_file(os.path.join(p7z_output,filename),filename)
                        office_meta_hash["file"].append(new_file)
                else:
                        office_meta_hash["file"]=[] 
                        new_file = get_basic_stuff_from_file(os.path.join(p7z_output,filename),filename)
                        office_meta_hash["file"].append(new_file)




        call(["rm","-r",folder_path]) 
        return office_meta_hash
