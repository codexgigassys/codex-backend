# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os, sys
source_path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
sys.path.insert(0,source_path)
from Sample import Sample
from subprocess import check_output
import binascii

from PlugIns.PlugIn import PlugIn
from Modules.PEFileModule import PEFileModule
import pefile
from pyasn1.codec.der import encoder, decoder
from pyasn1_modules import rfc2315

class CertficatePlug(PlugIn):
    def __init__(self,sample=None):
        PlugIn.__init__(self,sample)

    def getPath(self):
        return "particular_header.certificate"

    def getName(self):
        return "certificate"

    def getVersion(self):
        return 2

    def process(self):
        raw_certificate_file = "./certPlug.temp"
        pelib=self._getLibrary(PEFileModule().getName())
        if(pelib==None):return ""

        # reset the offset to the table containing the signature
        sigoff = 0
        # reset the lenght of the table
        siglen = 0

        # search for the 'IMAGE_DIRECTORY_ENTRY_SECURITY' directory
        # probably there is a direct way to find that directory
        # but I am not aware of it at the moment
        found=False
        for s in pelib.__structures__:
            if s.name == 'IMAGE_DIRECTORY_ENTRY_SECURITY':
                # set the offset to the signature table
                sigoff = s.VirtualAddress
                # set the length of the table
                siglen = s.Size
                #print(siglen)
                if (siglen>=8):
                    found=True

        if not found: return {}

        bin_data=self.sample.getBinary()
        totsize=len(bin_data)

        if sigoff < totsize:
            # hmmm, okay we could possibly read this from the PE object
            # but is straightforward to just open the file again
            # as a file object
            #f = open(a,'rb')
            # move to the beginning of signature table
            #f.seek(sigoff)
            # read the signature table
            #thesig = f.read(siglen)
            thesig = bin_data[sigoff:(sigoff+siglen)]
            # close the file
            #f.close()

            # now the 'thesig' variable should contain the table with
            # the following structure
            #   DWORD       dwLength          - this is the length of bCertificate
            #   WORD        wRevision
            #   WORD        wCertificateType
            #   BYTE        bCertificate[dwLength] - this contains the PKCS7 signature
            #                                    with all the

            # lets dump only the PKCS7 signature (without checking the lenght with dwLength)

            res={}

            length_raw=thesig[:4]
            revision_raw=thesig[4:6]
            type_raw=thesig[6:8]
            raw_certificate=thesig[8:]

            res["length"]=int(binascii.hexlify(length_raw), 16)
            res["revision"]=int(binascii.hexlify(revision_raw), 16)
            res["type"]=int(binascii.hexlify(type_raw), 16)
            res["signed"]=True

            fd=open(raw_certificate_file,"w")
            fd.write(raw_certificate)
            fd.close()

            cmd=["openssl","pkcs7","-inform","DER","-print_certs","-text","-in",raw_certificate_file]
            try:
                output=check_output(cmd)
            except Exception, e:
                print str(e)
                return {}
            #print(output)


            certificates=[]
            one_cert={}
            iterator=iter(output.split('\n'))

            while True:
                try:
                    actual=iterator.next().strip()
                    #print(actual)
                except:
                    break
                if(actual.find("Certificate:")==0):
                    if(len(one_cert)>0):
                        certificates.append(one_cert)
                        one_cert={}
                elif(actual.find("Serial Number:")==0):
                    if(len(actual)>len("Serial Number:")+2):
                        hasta=actual.find("(")
                        serial=actual[len("Serial Number:"):hasta]
                        serial=serial.strip()
                    else:
                        serial=iterator.next().strip()
                    #print("##%s##"%serial)
                    one_cert["serial"]=serial.lower()
                elif(actual.find("Issuer:")==0):
                    s_pos=actual.find(", O=")
                    if(s_pos>=0):
                        f_pos=actual.find(',',s_pos+1)
                        if(f_pos<0):f_pos=None
                        issuer_o=actual[s_pos+4:f_pos]
                    else:
                        issuer_o=""
                    one_cert["issuer"]=issuer_o.lower()
                elif(actual.find("Validity")==0):
                    val_in=iterator.next().strip()
                    val_fin=iterator.next().strip()
                    one_cert["validity_beg"]=val_in[12:].lower()
                    one_cert["validity_end"]=val_fin[12:].lower()
                elif(actual.find("Subject:")==0):
                    s_pos=actual.find(", O=")
                    if(s_pos>=0):
                        f_pos=actual.find(',',s_pos+1)
                        if(f_pos<0):f_pos=None
                        subject_o=actual[s_pos+4:f_pos]
                    else:
                        subject_o=""
                    one_cert["subject"]=subject_o.lower()

            if(len(one_cert)>0):
                certificates.append(one_cert)
            res["certificates"]=certificates
            return res

        else:
            return {}

    def process2(self):
        pe=self._getLibrary(PEFileModule().getName())
        if(pe==None):return ""
        #  get the security directory entry
        address = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].VirtualAddress

        if address > 0:
            # Always in DER format AFAIK
            derData = pe.write()[address + 8:]
        else:
            print("address 0")
            return

        (contentInfo, rest) = decoder.decode(derData, asn1Spec=rfc2315.ContentInfo())

        contentType = contentInfo.getComponentByName('contentType')

        if contentType == rfc2315.signedData:
            signedData = decode(contentInfo.getComponentByName('content'),asn1Spec=rfc2315.SignedData())

        for sd in signedData:
            if sd == '': continue

            signerInfos = sd.getComponentByName('signerInfos')
            for si in signerInfos:
                issuerAndSerial = si.getComponentByName('issuerAndSerialNumber')
                issuer = issuerAndSerial.getComponentByName('issuer').getComponent()
                for i in issuer:
                    for r in i:
                        at = r.getComponentByName('type')
                        if rfc2459.id_at_countryName == at:
                            cn = decode(r.getComponentByName('value'),asn1Spec=rfc2459.X520countryName())
                            print(cn[0])
                        elif rfc2459.id_at_organizationName == at:
                            on = decode(r.getComponentByName('value'),asn1Spec=rfc2459.X520OrganizationName())
                            print(on[0].getComponent())
                        elif rfc2459.id_at_organizationalUnitName == at:
                            ou = decode(r.getComponentByName('value'),asn1Spec=rfc2459.X520OrganizationalUnitName())
                            print(ou[0].getComponent())
                        elif rfc2459.id_at_commonName == at:
                            cn = decode(r.getComponentByName('value'),asn1Spec=rfc2459.X520CommonName())
                            print(cn[0].getComponent())
                        else:
                            print at



if __name__=="__main__":
    data=open(source_path+"/Test_files/certificate5.codex","rb").read()
    sample=Sample()
    sample.setBinary(data)
    modules={}
    pfm=PEFileModule()
    modules[pfm.getName()]=pfm
    plug=CertficatePlug()
    plug.setModules(modules)
    plug.setSample(sample)
    res=plug.process()
    print(res)
    #fd=open("certficado.out","wb")
    #fd.write(res["bCertificate"])
    #fd.close()
