# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile


class HeadersPlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getPath(self):
        return "particular_header.headers"

    def getName(self):
        return "headers"

    def getVersion(self):
        return 2

    def process(self):
        pelib = self._getLibrary(PEFileModule().getName())
        if(pelib == None):
            return ""

        dos = {}
        dos["magic"] = self._normalize(pelib.DOS_HEADER.e_magic)
        dos["cblp"] = self._normalize(pelib.DOS_HEADER.e_cblp)
        dos["cp"] = self._normalize(pelib.DOS_HEADER.e_cp)
        dos["crlc"] = self._normalize(pelib.DOS_HEADER.e_crlc)
        dos["cparhdr"] = self._normalize(pelib.DOS_HEADER.e_cparhdr)
        dos["minalloc"] = self._normalize(pelib.DOS_HEADER.e_minalloc)
        dos["maxalloc"] = self._normalize(pelib.DOS_HEADER.e_maxalloc)
        dos["ss"] = self._normalize(pelib.DOS_HEADER.e_ss)
        dos["sp"] = self._normalize(pelib.DOS_HEADER.e_sp)
        dos["csum"] = self._normalize(pelib.DOS_HEADER.e_csum)
        dos["ip"] = self._normalize(pelib.DOS_HEADER.e_ip)
        dos["cs"] = self._normalize(pelib.DOS_HEADER.e_cs)
        dos["lfarlc"] = self._normalize(pelib.DOS_HEADER.e_lfarlc)
        dos["ovno"] = self._normalize(pelib.DOS_HEADER.e_ovno)
        dos["res"] = self._normalize(pelib.DOS_HEADER.e_res)
        dos["oemid"] = self._normalize(pelib.DOS_HEADER.e_oemid)
        dos["oeminfo"] = self._normalize(pelib.DOS_HEADER.e_oeminfo)
        dos["res2"] = self._normalize(pelib.DOS_HEADER.e_res2)
        dos["lfanew"] = self._normalize(pelib.DOS_HEADER.e_lfanew)

        nt = {}
        nt["Signature"] = self._normalize(pelib.NT_HEADERS.Signature)

        fh = {}
        fh["Machine"] = self._normalize(pelib.FILE_HEADER.Machine)
        fh["NumberOfSections"] = self._normalize(
            pelib.FILE_HEADER.NumberOfSections)
        fh["TimeDateStamp"] = self._normalize(pelib.FILE_HEADER.TimeDateStamp)
        fh["PointerToSymbolTable"] = self._normalize(
            pelib.FILE_HEADER.PointerToSymbolTable)
        fh["NumberOfSymbols"] = self._normalize(
            pelib.FILE_HEADER.NumberOfSymbols)
        fh["SizeOfOptionalHeader"] = self._normalize(
            pelib.FILE_HEADER.SizeOfOptionalHeader)
        fh["Characteristics"] = self._normalize(
            pelib.FILE_HEADER.Characteristics)

        oh = {}
        oh["Magic"] = self._normalize(pelib.OPTIONAL_HEADER.Magic)
        oh["MajorLinkerVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MajorLinkerVersion)
        oh["MinorLinkerVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MinorLinkerVersion)
        oh["SizeOfCode"] = self._normalize(pelib.OPTIONAL_HEADER.SizeOfCode)
        oh["SizeOfInitializedData"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfInitializedData)
        oh["SizeOfUninitializedData"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfUninitializedData)
        oh["AddressOfEntryPoint"] = self._normalize(
            pelib.OPTIONAL_HEADER.AddressOfEntryPoint)
        oh["BaseOfCode"] = self._normalize(pelib.OPTIONAL_HEADER.BaseOfCode)
        oh["ImageBase"] = self._normalize(pelib.OPTIONAL_HEADER.ImageBase)
        oh["SectionAlignment"] = self._normalize(
            pelib.OPTIONAL_HEADER.SectionAlignment)
        oh["FileAlignment"] = self._normalize(
            pelib.OPTIONAL_HEADER.FileAlignment)
        oh["MajorOperatingSystemVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MajorOperatingSystemVersion)
        oh["MinorOperatingSystemVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MinorOperatingSystemVersion)
        oh["MajorImageVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MajorImageVersion)
        oh["MinorImageVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MinorImageVersion)
        oh["MajorSubsystemVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MajorSubsystemVersion)
        oh["MinorSubsystemVersion"] = self._normalize(
            pelib.OPTIONAL_HEADER.MinorSubsystemVersion)
        oh["Reserved1"] = self._normalize(pelib.OPTIONAL_HEADER.Reserved1)
        oh["SizeOfImage"] = self._normalize(pelib.OPTIONAL_HEADER.SizeOfImage)
        oh["SizeOfHeaders"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfHeaders)
        oh["CheckSum"] = self._normalize(pelib.OPTIONAL_HEADER.CheckSum)
        oh["Subsystem"] = self._normalize(pelib.OPTIONAL_HEADER.Subsystem)
        oh["DllCharacteristics"] = self._normalize(
            pelib.OPTIONAL_HEADER.DllCharacteristics)
        oh["SizeOfStackReserve"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfStackReserve)
        oh["SizeOfStackCommit"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfStackCommit)
        oh["SizeOfHeapReserve"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfHeapReserve)
        oh["SizeOfHeapCommit"] = self._normalize(
            pelib.OPTIONAL_HEADER.SizeOfHeapCommit)
        oh["LoaderFlags"] = self._normalize(pelib.OPTIONAL_HEADER.LoaderFlags)
        oh["NumberOfRvaAndSizes"] = self._normalize(
            pelib.OPTIONAL_HEADER.NumberOfRvaAndSizes)

        res = {}
        res["dos_header"] = dos
        res["nt_header"] = nt
        res["file_header"] = fh
        res["optional_header"] = oh

        return res
