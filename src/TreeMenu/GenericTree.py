# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.

tree_element={"name":"Generic","children":[
    {"name":"Hash","id":1,"type":"string","example":"MD5, SHA1, SHA2","children":[],"searchable":True,"projectable":True, "call_func": "", "lower": True},
    {"name":"Description","id":146,"type":"string","children":[],"searchable":False,"projectable":True, "call_func": "", "lower": False},
    {"name":"Size","id":4,"type":"number","min":0,"example":103140,"children":[],"searchable":True,"projectable":True, "call_func": ""},
    {"name":"Mime type", "id": 5, "type": "string", "example": "application/x-dosexec", "children": [],"searchable":True,"projectable":True, "call_func": "", "lower": True},
    {"name":"AntiVirus","children":[
        {"name":"AV signature","id":10000,"type":"string","example":"trojan","children":[],"searchable":True,"projectable":False},
        ]}
    ]}

id_element={
    1:{"path":"hash.md5","type":"string", "do": "clean_hash" },
    2:{"path":"hash.sha1","type":"string", "do": "clean_hash" },
    3:{"path":"hash.sha2","type":"string", "do": "clean_hash" },
    146:{"path":"description","type":"string"},
    4:{"path":"size","type":"int"},
    5:{"path":"mime_type","type":"string"},
    10:{"path":"fuzzy_hash","type":"string"},
    11:{},    
    10000:{"path":"scans.result","type":"string"}  # for searcher greater than 10000
    }
