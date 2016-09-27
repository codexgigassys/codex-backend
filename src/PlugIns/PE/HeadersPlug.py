# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile

class HeadersPlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.headers"

    def getName(self):
        return "headers"

    def getVersion(self):
        return 2

    def process(self):
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        dos={}
        dos["magic"]=pelib.DOS_HEADER.e_magic
        dos["cblp"]=pelib.DOS_HEADER.e_cblp
        dos["cp"]=pelib.DOS_HEADER.e_cp
        dos["crlc"]=pelib.DOS_HEADER.e_crlc
        dos["cparhdr"]=pelib.DOS_HEADER.e_cparhdr
        dos["minalloc"]=pelib.DOS_HEADER.e_minalloc
        dos["maxalloc"]=pelib.DOS_HEADER.e_maxalloc
        dos["ss"]=pelib.DOS_HEADER.e_ss
        dos["sp"]=pelib.DOS_HEADER.e_sp
        dos["csum"]=pelib.DOS_HEADER.e_csum
        dos["ip"]=pelib.DOS_HEADER.e_ip
        dos["cs"]=pelib.DOS_HEADER.e_cs
        dos["lfarlc"]=pelib.DOS_HEADER.e_lfarlc
        dos["ovno"]=pelib.DOS_HEADER.e_ovno
        dos["res"]=self._normalize(pelib.DOS_HEADER.e_res)
        dos["oemid"]=pelib.DOS_HEADER.e_oemid
        dos["oeminfo"]=pelib.DOS_HEADER.e_oeminfo
        dos["res2"]=self._normalize(pelib.DOS_HEADER.e_res2)
        dos["lfanew"]=pelib.DOS_HEADER.e_lfanew

        nt={}
        nt["Signature"]=self._normalize(pelib.NT_HEADERS.Signature)

        fh={}
        fh["Machine"]=pelib.FILE_HEADER.Machine
        fh["NumberOfSections"]=pelib.FILE_HEADER.NumberOfSections
        fh["TimeDateStamp"]=pelib.FILE_HEADER.TimeDateStamp
        fh["PointerToSymbolTable"]=pelib.FILE_HEADER.PointerToSymbolTable
        fh["NumberOfSymbols"]=pelib.FILE_HEADER.NumberOfSymbols
        fh["SizeOfOptionalHeader"]=pelib.FILE_HEADER.SizeOfOptionalHeader
        fh["Characteristics"]=pelib.FILE_HEADER.Characteristics

        oh={}
        oh["Magic"]=pelib.OPTIONAL_HEADER.Magic
        oh["MajorLinkerVersion"]=pelib.OPTIONAL_HEADER.MajorLinkerVersion
        oh["MinorLinkerVersion"]=pelib.OPTIONAL_HEADER.MinorLinkerVersion
        oh["SizeOfCode"]=pelib.OPTIONAL_HEADER.SizeOfCode
        oh["SizeOfInitializedData"]=pelib.OPTIONAL_HEADER.SizeOfInitializedData
        oh["SizeOfUninitializedData"]=pelib.OPTIONAL_HEADER.SizeOfUninitializedData
        oh["AddressOfEntryPoint"]=pelib.OPTIONAL_HEADER.AddressOfEntryPoint
        oh["BaseOfCode"]=pelib.OPTIONAL_HEADER.BaseOfCode
        oh["ImageBase"]=pelib.OPTIONAL_HEADER.ImageBase
        oh["SectionAlignment"]=pelib.OPTIONAL_HEADER.SectionAlignment
        oh["FileAlignment"]=pelib.OPTIONAL_HEADER.FileAlignment
        oh["MajorOperatingSystemVersion"]=pelib.OPTIONAL_HEADER.MajorOperatingSystemVersion
        oh["MinorOperatingSystemVersion"]=pelib.OPTIONAL_HEADER.MinorOperatingSystemVersion
        oh["MajorImageVersion"]=pelib.OPTIONAL_HEADER.MajorImageVersion
        oh["MinorImageVersion"]=pelib.OPTIONAL_HEADER.MinorImageVersion
        oh["MajorSubsystemVersion"]=pelib.OPTIONAL_HEADER.MajorSubsystemVersion
        oh["MinorSubsystemVersion"]=pelib.OPTIONAL_HEADER.MinorSubsystemVersion
        oh["Reserved1"]=pelib.OPTIONAL_HEADER.Reserved1
        oh["SizeOfImage"]=pelib.OPTIONAL_HEADER.SizeOfImage
        oh["SizeOfHeaders"]=pelib.OPTIONAL_HEADER.SizeOfHeaders
        oh["CheckSum"]=pelib.OPTIONAL_HEADER.CheckSum
        oh["Subsystem"]=pelib.OPTIONAL_HEADER.Subsystem
        oh["DllCharacteristics"]=pelib.OPTIONAL_HEADER.DllCharacteristics
        oh["SizeOfStackReserve"]=pelib.OPTIONAL_HEADER.SizeOfStackReserve
        oh["SizeOfStackCommit"]=pelib.OPTIONAL_HEADER.SizeOfStackCommit
        oh["SizeOfHeapReserve"]=pelib.OPTIONAL_HEADER.SizeOfHeapReserve
        oh["SizeOfHeapCommit"]=pelib.OPTIONAL_HEADER.SizeOfHeapCommit
        oh["LoaderFlags"]=pelib.OPTIONAL_HEADER.LoaderFlags
        oh["NumberOfRvaAndSizes"]=pelib.OPTIONAL_HEADER.NumberOfRvaAndSizes

        res={}
        res["dos_header"]=dos
        res["nt_header"]=nt
        res["file_header"]=fh
        res["optional_header"]=oh

        return res
