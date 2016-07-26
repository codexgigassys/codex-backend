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

"""
##Example of certificate

Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            52:00:e5:aa:25:56:fc:1a:86:ed:96:c9:d4:4b:33:c7
    Signature Algorithm: sha1WithRSAEncryption
        Issuer: C=US, O=VeriSign, Inc., OU=VeriSign Trust Network, OU=(c) 2006 VeriSign, Inc. - For authorized use only, CN=VeriSign Class 3 Public Primary Certification Authority - G5
        Validity
            Not Before: Feb  8 00:00:00 2010 GMT
            Not After : Feb  7 23:59:59 2020 GMT
        Subject: C=US, O=VeriSign, Inc., OU=VeriSign Trust Network, OU=Terms of use at https://www.verisign.com/rpa (c)10, CN=VeriSign Class 3 Code Signing 2010 CA
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:f5:23:4b:5e:a5:d7:8a:bb:32:e9:d4:57:f7:ef:
                    e4:c7:26:7e:ad:19:98:fe:a8:9d:7d:94:f6:36:6b:
                    10:d7:75:81:30:7f:04:68:7f:cb:2b:75:1e:cd:1d:
                    08:8c:df:69:94:a7:37:a3:9c:7b:80:e0:99:e1:ee:
                    37:4d:5f:ce:3b:14:ee:86:d4:d0:f5:27:35:bc:25:
                    0b:38:a7:8c:63:9d:17:a3:08:a5:ab:b0:fb:cd:6a:
                    62:82:4c:d5:21:da:1b:d9:f1:e3:84:3b:8a:2a:4f:
                    85:5b:90:01:4f:c9:a7:76:10:7f:27:03:7c:be:ae:
                    7e:7d:c1:dd:f9:05:bc:1b:48:9c:69:e7:c0:a4:3c:
                    3c:41:00:3e:df:96:e5:c5:e4:94:71:d6:55:01:c7:
                    00:26:4a:40:3c:b5:a1:26:a9:0c:a7:6d:80:8e:90:
                    25:7b:cf:bf:3f:1c:eb:2f:96:fa:e5:87:77:c6:b5:
                    56:b2:7a:3b:54:30:53:1b:df:62:34:ff:1e:d1:f4:
                    5a:93:28:85:e5:4c:17:4e:7e:5b:fd:a4:93:99:7f:
                    df:cd:ef:a4:75:ef:ef:15:f6:47:e7:f8:19:72:d8:
                    2e:34:1a:a6:b4:a7:4c:7e:bd:bb:4f:0c:3d:57:f1:
                    30:d6:a6:36:8e:d6:80:76:d7:19:2e:a5:cd:7e:34:
                    2d:89
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Basic Constraints: critical
                CA:TRUE, pathlen:0
            X509v3 Certificate Policies: 
                Policy: 2.16.840.1.113733.1.7.23.3
                  CPS: https://www.verisign.com/cps
                  User Notice:
                    Explicit Text: https://www.verisign.com/rpa

            X509v3 Key Usage: critical
                Certificate Sign, CRL Sign
            1.3.6.1.5.5.7.1.12: 
                0_.].[0Y0W0U..image/gif0!0.0...+..............k...j.H.,{..0%.#http://logo.verisign.com/vslogo.gif
            X509v3 CRL Distribution Points: 

                Full Name:
                  URI:http://crl.verisign.com/pca3-g5.crl

            Authority Information Access: 
                OCSP - URI:http://ocsp.verisign.com

            X509v3 Extended Key Usage: 
                TLS Web Client Authentication, Code Signing
            X509v3 Subject Alternative Name: 
                DirName:/CN=VeriSignMPKI-2-8
            X509v3 Subject Key Identifier: 
                CF:99:A9:EA:7B:26:F4:4B:C9:8E:8F:D7:F0:05:26:EF:E3:D2:A7:9D
            X509v3 Authority Key Identifier: 
                keyid:7F:D3:65:A7:C2:DD:EC:BB:F0:30:09:F3:43:39:FA:02:AF:33:31:33

    Signature Algorithm: sha1WithRSAEncryption
         56:22:e6:34:a4:c4:61:cb:48:b9:01:ad:56:a8:64:0f:d9:8c:
         91:c4:bb:cc:0c:e5:ad:7a:a0:22:7f:df:47:38:4a:2d:6c:d1:
         7f:71:1a:7c:ec:70:a9:b1:f0:4f:e4:0f:0c:53:fa:15:5e:fe:
         74:98:49:24:85:81:26:1c:91:14:47:b0:4c:63:8c:bb:a1:34:
         d4:c6:45:e8:0d:85:26:73:03:d0:a9:8c:64:6d:dc:71:92:e6:
         45:05:60:15:59:51:39:fc:58:14:6b:fe:d4:a4:ed:79:6b:08:
         0c:41:72:e7:37:22:06:09:be:23:e9:3f:44:9a:1e:e9:61:9d:
         cc:b1:90:5c:fc:3d:d2:8d:ac:42:3d:65:36:d4:b4:3d:40:28:
         8f:9b:10:cf:23:26:cc:4b:20:cb:90:1f:5d:8c:4c:34:ca:3c:
         d8:e5:37:d6:6f:a5:20:bd:34:eb:26:d9:ae:0d:e7:c5:9a:f7:
         a1:b4:21:91:33:6f:86:e8:58:bb:25:7c:74:0e:58:fe:75:1b:
         63:3f:ce:31:7c:9b:8f:1b:96:9e:c5:53:76:84:5b:9c:ad:91:
         fa:ac:ed:93:ba:5d:c8:21:53:c2:82:53:63:af:12:0d:50:87:
         11:1b:3d:54:52:96:8a:2c:9c:3d:92:1a:08:9a:05:2e:c7:93:
         a5:48:91:d3
-----BEGIN CERTIFICATE-----
MIIGCjCCBPKgAwIBAgIQUgDlqiVW/BqG7ZbJ1EszxzANBgkqhkiG9w0BAQUFADCB
yjELMAkGA1UEBhMCVVMxFzAVBgNVBAoTDlZlcmlTaWduLCBJbmMuMR8wHQYDVQQL
ExZWZXJpU2lnbiBUcnVzdCBOZXR3b3JrMTowOAYDVQQLEzEoYykgMjAwNiBWZXJp
U2lnbiwgSW5jLiAtIEZvciBhdXRob3JpemVkIHVzZSBvbmx5MUUwQwYDVQQDEzxW
ZXJpU2lnbiBDbGFzcyAzIFB1YmxpYyBQcmltYXJ5IENlcnRpZmljYXRpb24gQXV0
aG9yaXR5IC0gRzUwHhcNMTAwMjA4MDAwMDAwWhcNMjAwMjA3MjM1OTU5WjCBtDEL
MAkGA1UEBhMCVVMxFzAVBgNVBAoTDlZlcmlTaWduLCBJbmMuMR8wHQYDVQQLExZW
ZXJpU2lnbiBUcnVzdCBOZXR3b3JrMTswOQYDVQQLEzJUZXJtcyBvZiB1c2UgYXQg
aHR0cHM6Ly93d3cudmVyaXNpZ24uY29tL3JwYSAoYykxMDEuMCwGA1UEAxMlVmVy
aVNpZ24gQ2xhc3MgMyBDb2RlIFNpZ25pbmcgMjAxMCBDQTCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAPUjS16l14q7MunUV/fv5Mcmfq0ZmP6onX2U9jZr
ENd1gTB/BGh/yyt1Hs0dCIzfaZSnN6Oce4DgmeHuN01fzjsU7obU0PUnNbwlCzin
jGOdF6MIpauw+81qYoJM1SHaG9nx44Q7iipPhVuQAU/Jp3YQfycDfL6ufn3B3fkF
vBtInGnnwKQ8PEEAPt+W5cXklHHWVQHHACZKQDy1oSapDKdtgI6QJXvPvz8c6y+W
+uWHd8a1VrJ6O1QwUxvfYjT/HtH0WpMoheVMF05+W/2kk5l/383vpHXv7xX2R+f4
GXLYLjQaprSnTH69u08MPVfxMNamNo7WgHbXGS6lzX40LYkCAwEAAaOCAf4wggH6
MBIGA1UdEwEB/wQIMAYBAf8CAQAwcAYDVR0gBGkwZzBlBgtghkgBhvhFAQcXAzBW
MCgGCCsGAQUFBwIBFhxodHRwczovL3d3dy52ZXJpc2lnbi5jb20vY3BzMCoGCCsG
AQUFBwICMB4aHGh0dHBzOi8vd3d3LnZlcmlzaWduLmNvbS9ycGEwDgYDVR0PAQH/
BAQDAgEGMG0GCCsGAQUFBwEMBGEwX6FdoFswWTBXMFUWCWltYWdlL2dpZjAhMB8w
BwYFKw4DAhoEFI/l0xqGrI2Oa8PPgGrUSBgsexkuMCUWI2h0dHA6Ly9sb2dvLnZl
cmlzaWduLmNvbS92c2xvZ28uZ2lmMDQGA1UdHwQtMCswKaAnoCWGI2h0dHA6Ly9j
cmwudmVyaXNpZ24uY29tL3BjYTMtZzUuY3JsMDQGCCsGAQUFBwEBBCgwJjAkBggr
BgEFBQcwAYYYaHR0cDovL29jc3AudmVyaXNpZ24uY29tMB0GA1UdJQQWMBQGCCsG
AQUFBwMCBggrBgEFBQcDAzAoBgNVHREEITAfpB0wGzEZMBcGA1UEAxMQVmVyaVNp
Z25NUEtJLTItODAdBgNVHQ4EFgQUz5mp6nsm9EvJjo/X8AUm7+PSp50wHwYDVR0j
BBgwFoAUf9Nlp8Ld7LvwMAnzQzn6Aq8zMTMwDQYJKoZIhvcNAQEFBQADggEBAFYi
5jSkxGHLSLkBrVaoZA/ZjJHEu8wM5a16oCJ/30c4Si1s0X9xGnzscKmx8E/kDwxT
+hVe/nSYSSSFgSYckRRHsExjjLuhNNTGRegNhSZzA9CpjGRt3HGS5kUFYBVZUTn8
WBRr/tSk7XlrCAxBcuc3IgYJviPpP0SaHulhncyxkFz8PdKNrEI9ZTbUtD1AKI+b
EM8jJsxLIMuQH12MTDTKPNjlN9ZvpSC9NOsm2a4N58Wa96G0IZEzb4boWLslfHQO
WP51G2M/zjF8m48blp7FU3aEW5ytkfqs7ZO6XcghU8KCU2OvEg1QhxEbPVRSloos
nD2SGgiaBS7Hk6VIkdM=
-----END CERTIFICATE-----
"""
