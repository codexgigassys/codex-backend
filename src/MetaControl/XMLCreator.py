# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import xml.etree.cElementTree as XML
import os

class XMLCreator():
    def __init__(self):
        pass

    def __delete__(self):
        pass


    def serialize(self,node):
        ser=XML.tostring(node)
        return ser

    def parse(self,meta_plain):
        try:
            root=XML.fromstring(meta_plain)
            dic=self._iterateNode(root)
            return dic
        except Exception, e:
            print str(e)
            return {}

    def appendValueFromDictionary(self,node,dic,value):
        n=XML.SubElement(node,value)
        n.text=str(dic[value])

    def saveToFile(self,xml_node,file_name):
        tree = XML.ElementTree(xml_node)
        tree.write("../DB/metadata/"+str(file_name)+".xml")
        return 0

    def createXMLNode(self,node_name,dic):
        root = XML.Element(node_name)
        self.appendAll(root,dic)
        return root

    def appendAll(self,node,contenedor):
        tipo=type(contenedor)
        if(tipo==type({})):     # appends to a dictionary
            for d in contenedor:
                n=XML.SubElement(node,d)
                self.appendAll(n,contenedor[d])
        elif(tipo==type([])):    # appends to a list
            for v in contenedor:
                n=XML.SubElement(node,"item")
                n.text=v
        else:
            node.text=str(contenedor) # saves a value

        #return node

    def readAll(self,file_name):
        try:
            tree=XML.parse("../DB/metadata/"+str(file_name)+".xml")
            root=tree.getroot()
            dic=self._iterateNode(root)
            return dic
        except Exception, e:
            print str(e)
            return {}


    def _iterateNode(self,node):
        dic={}
        lista=[]
        for sub in node:
            text=sub.text
            if(text==None):
                dic[sub.tag]=self._iterateNode(sub)
            else:
                if(sub.tag=="item"):
                    lista.append(text)
                else:
                    dic[sub.tag]=text
        if(len(lista)>0):
            return lista
        return dic


#****************TEST_CODE******************

TEST="-test_XMLCreator"
def testCode():
    #------------------------------------------------------------------
    dic={}
    dic["pepe"]="pepe"
    lista=[]
    lista.append("one thing")
    lista.append("other thing")
    dic["lista"]=lista
    xml=XMLCreator()
    node=xml.createXMLNode("principal_node",dic)
    ser=xml.serialize(node)
    print(ser)

    #------------------------------------------------------------------
    #~ xml=XMLCreator()
    #~ dic=xml.readAll("filename")
    #~ print(dic)
    #------------------------------------------------------------------
    #~ xml=XMLCreator()
    #~ data=open("test.xml","r").read()
    #~ dic=xml.parse(data)
    #~ print(dic)


#***********************TEST***************************
import sys
import traceback
if(len(sys.argv)>=2):
    if(sys.argv[1]==TEST):
        try:
            print("######## Test of " + str(sys.argv[0])+" ########")
            testCode()

        except:
            print(traceback.format_exc())
        raw_input("Press a key...")

