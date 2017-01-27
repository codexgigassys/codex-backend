import os
import sys
path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.insert(0, path)
import pymongo
import traceback

from db_pool import *



index_list = [
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.imports.functions",pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("size", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.name", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.size_of_raw_data", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.headers.file_header.TimeDateStamp", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.imports.lib", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.virtual_size", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.size_raw_data", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.hidden_imports", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.hidden_dll", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.res_entries.size", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.emails", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.urls", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.domains", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.ips", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.strings.interesting", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.exports.symbols.name", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.LegalCopyright", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.LangID", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.InternalName", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.CompanyName", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.ProductName", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.FileDescription", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.OriginalFilename", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.string_file_info.LegalTrademarks", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.certificate.certificates.serial", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("date", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.res_entries.sha1", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.md5", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.sha1", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.sections.sha2", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("file_id", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("hash.md5", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("hash.sha2", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("mime_type", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("hash.sha1", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.headers.optional_header.AddressOfEntryPoint", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("particular_header.version.fixed_file_info.Signature", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"meta_container", "keys":[("dynamic.sha1", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"imports_tree", "keys":[("function_name", pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"imports_tree", "keys":[("dll_name", pymongo.ASCENDING),("function_name",pymongo.ASCENDING)]},
    {"db":"DB_metadata", "coll":"av_analysis", "keys":[("sha1", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"av_analysis", "keys":[("scans.result", pymongo.ASCENDING)]},
    {"db":"DB_versions", "coll":"version_container", "keys":[("file_id", pymongo.HASHED)]},
    {"db":"DB_metadata", "coll":"tasks", "keys":[("task_id", pymongo.HASHED)]},
    ]

def check_if_index_exist(index,list_indexes):
    for key,value in list_indexes.items():
        if(set(index)==set(value.get('key'))):
            return True
    return False


if __name__ == '__main__':
    db_ip = env["metadata"]["host"]
    db_port = env["metadata"]["port"]

    for index in index_list:
        client=pymongo.MongoClient(db_ip,db_port)
        db=client[index["db"]]
        collection=db[index["coll"]]
        list_of_indexes = collection.index_information()
        try:
            if(not check_if_index_exist(index["keys"],list_of_indexes)):
                print("Creating %s index" % index["keys"])
                collection.create_index(index["keys"], sparse=True, background=False)
        except Exception, e :
            print "Exception"
            print str(e)
            print(traceback.format_exc())

