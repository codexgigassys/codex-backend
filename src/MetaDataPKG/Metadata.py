# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
class Metadata():
    def __init__(self):
        self.data={}
        self.empty=True
    
    def isEmpty(self):
        return self.empty
                        
    def setData(self,data):
        self.empty=False
        self.data=data
        
    def getData(self):
        return self.data
        
    def getValue(self,source):
        path=source.split('.')
        root=self.data
        for p in path:
            try:
                root=root.get(p)
                if(root==None): return None
            except KeyboardInterrupt:raise KeyboardInterrupt
            except Exception, e:
                print str(e)
                return None
        return root

    def setValue(self,source,value):
        self.empty=False
        path=source.split('.')
        root=self.data
        for p in path[:-1]:
            n=root.get(p)
            if ( n!= None ):root=n
            else:
                aux={}
                root[p]=aux
                root=aux
        root[path[-1]]=value
            
    
#m=Metadata()
#m.setData({"pepe":"nosenose","manaos":"horrriibleeee","aver":{"otra":"ahoraSi"}})
#m.setValue("pepe","nosenose")
#m.setValue("aver.otra","ahoraSi")
#m.setValue("aver.otra2","tambien")

#print(m.getValue("pepe"))
#print(m.getValue("pepe2"))
#print(m.getValue("manaos"))
#print(m.getValue("aver"))
#print(m.getValue("aver.otra"))
#print(m.getValue("aver.otra2"))


