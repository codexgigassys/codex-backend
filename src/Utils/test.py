# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
#Utilitario para testear codigo
def test(TEST,function):
    import sys
    import traceback
    if(len(sys.argv)>=2):
        if(sys.argv[1]==TEST):
            try:
                print("[--------------- Test of " + str(sys.argv[0])+" -------------]")
                function()
            except Exception,e:
                print (str(e))
                print("####### Error detected #######")
                print("")
                print(traceback.format_exc())
                print("")
                print("###### End of log ######")
            #raw_input("Press a key...")

#****************TEST_CODE******************
def probando():
    print("testing")

def testCode():
    test("-test_test",probando)

#****************TEST_EXECUTE******************
test("-test_test",testCode)
