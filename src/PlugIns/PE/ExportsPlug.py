# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
import sys
source_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, source_path)


from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile
from Sample import Sample


class ExportsPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.exports"

    def getName(self):
        return "exports"

    def getVersion(self):
        return 1

    def process(self):
        pelib = self._getLibrary(PEFileModule().getName())
        if(pelib == None):
            return ""

        ret = {}

        # print(dir(pelib.DIRECTORY_ENTRY_EXPORT))
        # print(dir(pelib.DIRECTORY_ENTRY_EXPORT.symbols))

        if not hasattr(pelib, 'DIRECTORY_ENTRY_EXPORT'):
            return ret

        ret["characteristics"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.Characteristics
        ret["timeDateStamp"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.TimeDateStamp
        ret["majorVersion"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.MajorVersion
        ret["minorVersion"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.MinorVersion
        ret["name"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.Name
        ret["base"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.Base
        ret["numberOfFunctions"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.NumberOfFunctions
        ret["numberOfNames"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.NumberOfNames
        ret["addressOfFunctions"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.AddressOfFunctions
        ret["AddressOfNames"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.AddressOfNames
        ret["AddressOfOrdinals"] = pelib.DIRECTORY_ENTRY_EXPORT.struct.AddressOfNameOrdinals

        symbols = []
        # print(dir(pelib.DIRECTORY_ENTRY_EXPORT.symbols))
        for export in pelib.DIRECTORY_ENTRY_EXPORT.symbols:

            # print(dir(export))
            # print(export.address)
            # print(hex(export.address))

            symbol = {}

            symbol["ordinal"] = export.ordinal
            symbol["name"] = str(export.name).lower()
            symbol["RVA"] = export.address
            if(export.forwarder != None):
                if(export.forwarder.find('.') != -1):
                    symbol["forwarder_dll"] = repr(
                        str(export.forwarder).lower().split('.')[0] + ".dll")
                    symbol["forwarder_function"] = repr(
                        str(export.forwarder).lower().split('.')[1])

            # symbol["address"]=hex(export.address)
            # symbol["address_offset"]=hex(export.address_offset)
            # symbol["forwarder_offset"]=hex(export.forwarder_offset)
            # symbol["name_offset"]=hex(export.name_offset)
            # symbol["ordinal_offset"]=hex(export.ordinal_offset)
            # symbol["pe"]=export.pe
            symbols.append(symbol)

            # print(symbol)
            # raw_input()

        ret["symbols"] = symbols

        return ret

if __name__ == "__main__":
    data = open(source_path + "/Test_files/kernel32.dll", "rb").read()
    sample = Sample()
    sample.setBinary(data)
    modules = {}
    pfm = PEFileModule()
    modules[pfm.getName()] = pfm
    plug = ExportsPlug()
    plug.setModules(modules)
    plug.setSample(sample)
    res = plug.process()
    # print(res)
