# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import pefile
import math

class PEHeaderReader():
    #def __init__(self,file):
    #    self.pe=pefile.PE(file,fast_load=False)
    #    #self.pe=pefile.PE(file,fast_load=True)

    def __init__(self,data):
        self.pe=None
        try:
            self.pe=pefile.PE(data=data,fast_load=True)
        except Exception, e:
            print str(e)
            return None

        #~ try:
            #~ self.pe=pefile.PE(data=data,fast_load=False)
        #~ except:
            #~ self.pe=pefile.PE(data=data,fast_load=True)


    def get_import_size(self):
        #self.pe.parse_data_directories() # si tiene fast load
        sizes=[]
        for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
            sizes.append(len(entry.imports))
        return sizes

    def get_import_size_stats(self):
        #self.pe.parse_data_directories() # si tiene fast load
        total=0
        if (self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']].VirtualAddress == 0):
            return 0,0,0
        for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
            total=total+len(entry.imports)
            #print entry.dll
            #for imp in entry.imports:
            #print '\t', hex(imp.address), imp.name

        cant_librerias=(len(self.pe.DIRECTORY_ENTRY_IMPORT))
        total_imports=total
        promedio=total/cant_librerias

        return total_imports,cant_librerias,promedio

    def get_section_stats(self):
        real_sum=0
        virtual_sum=0
        w_e=0
        w_real_sum=0
        w_virtual_sum=0
        for section in self.pe.sections:
            real=int(hex(section.SizeOfRawData),16)
            virtual=int(hex(section.Misc_VirtualSize ),16)
            real_sum+=real
            virtual_sum+=virtual
            #print(hex(section.Characteristics))
            if ( section.__dict__.get('IMAGE_SCN_MEM_WRITE', False)  and
                    section.__dict__.get('IMAGE_SCN_MEM_EXECUTE', False) ):
                #print("Write Exe")
                w_e+=1
                w_real_sum+=real
                w_virtual_sum+=virtual

            #print (section.Name, real,virtual,rate)
        #print("")


        return real,virtual,w_e,w_real_sum,w_virtual_sum

    def getArquitecture(self):
        try:

            if(self.pe.OPTIONAL_HEADER.Magic==int("0x020B",16)):
                return ("PE+")
            elif(self.pe.OPTIONAL_HEADER.Magic==int("0x010B",16)):
                return ("PE")
            elif(self.pe.OPTIONAL_HEADER.Magic==int("0x0107",16)):
                return ("IMG_ROM")
            else:
                return "UNKNOWN"
        except:
            return "FORMAT"

        return None

    def getImports(self):
        if (self.pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']].VirtualAddress == 0):
            return None

        d={}
        #print(self.pe.DIRECTORY_ENTRY_IMPORT)
        for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
            aux=[]
            for i in range(len(entry.dll)):
                if(ord(entry.dll[i])>=128):
                    aux.append('.')
                else:
                    aux.append(entry.dll[i])

            dll_name="".join(aux)

            #print entry.dll
            #print entry.imports
            l=[]
            for imp in entry.imports:
                l.append(str(imp.name))
                #print '\t', hex(imp.address), imp.name
            d[unicode(str(dll_name),"utf-8")]=l

        return d

    def load(self):
        self.pe.parse_data_directories()

#****************TEST_CODE******************
import os,sys,shutil
import time

def testCode():

    file="../Test_files/test.exe"
    data=open(file,"rb").read()

    start_time=time.time()
    cr=PEHeaderReader(data=data)
    cr.load()
    total_imports,cant_librerias,promedio=cr.get_import_size_stats()
    real,virtual,w_e,w_real_sum,w_virtual_sum=cr.get_section_stats()
    elapsed=time.time()-start_time

    line1=str(total_imports)+"|"+str(cant_librerias)+"|"+str(promedio)
    line2=str(real)+"|"+str(virtual)+"|"+str(w_e)+"|"+str(w_real_sum)+"|"+str(w_virtual_sum)

    print(line1)
    print(line2)

    imp=cr.getImports()
    print(str(imp))
    print("Elapsed time: "+str(elapsed))


#****************TEST_EXECUTE******************
from test import test
test("-test_PEHeaderReader",testCode)
