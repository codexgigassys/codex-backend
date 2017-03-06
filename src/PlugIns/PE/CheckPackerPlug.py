# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn


class CheckPackerPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.packer_detection"

    def getName(self):
        return "packer_detection"

    def getVersion(self):
        return 2

    def process(self):
        entropy = self.sample.getLastValue("file_entropy")
        sections = self.sample.getLastValue("sections")
        imports = self.sample.getLastValue("imports")
        if(entropy == None or sections == None or imports == None):
            return "Unknown"
        flags = 0

        if (entropy >= 6.7):
            flags += 1

        real_sum = 0
        virtual_sum = 0
        we_sum = 0
        we_real_sum = 0
        we_virtual_sum = 0
        for s in sections:
            raw = s["size_raw_data"]
            vir = s["virtual_size"]
            we = s["write_executable"]
            real_sum += raw
            virtual_sum += vir
            if(we == "True"):
                we_sum += 1
                we_real_sum = raw
                we_virtual_sum += vir
        if(we_sum >= 1):
            flags += 1
            try:
                if((1.0 * we_virtual_sum / we_real_sum) >= 1):
                    flags += 1
            except Exception, e:
                print str(e)
                flags += 1
        try:
            if((1.0 * virual_sum / real_sum) >= 1):
                flags += 1
        except Exception, e:
            flags += 1

        cant_libs = len(imports)
        total_imports = 0
        for i in imports:
            try:
                total_imports += len(i["functions"])
            except Exception, e:
                print str(e)
                break

        if(cant_libs != 0):
            promedio = total_imports / cant_libs
            if(promedio <= 6 and promedio >= 1):
                flags += 1
        if(total_imports <= 35 and total_imports >= 1):
            flags += 1

        if(flags >= 4):
            return "True"
        return "False"
