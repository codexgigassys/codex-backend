# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from multiprocessing import Process
from multiprocessing import Semaphore

def processCall(semaphore,obj,function_to_execute,data):
    getattr(obj,function_to_execute)(data)
    semaphore.release()

class ProcessControl():
    def __init__(self,forks_number):
        self.forks_number=forks_number
        self.semaphore=Semaphore(self.forks_number)

    def execute(self,obj,function_to_execute,data):
        self.semaphore.acquire()
        #print("Launching new process")
        p=Process(target=processCall, args=(self.semaphore,obj,function_to_execute,data))
        p.start()


    def wait(self):
        for i in range(self.forks_number):
            self.semaphore.acquire()

#test##############################################

def test():
    import random
    import time

    class MyClass():
        def function_to_run(self,data):
            time.sleep(random.randint(0,3))
            print(data)

    simultaneus_workers=5
    pc=ProcessControl(simultaneus_workers)

    obj=MyClass()
    function="function_to_run"

    for data in range(0,10):
        pc.execute(obj,function,data)

    pc.wait()


if __name__ == "__main__":
    test()



