#http://stackoverflow.com/a/17718729
class Ram:
    def __init__(self):
        print "ram loaded"

    #returns a float from 0 to 1 with the % of free memory
    def free_percent(self):
        mem = self.memory()
        return float(mem['free'])/float(mem['total'])

    def memory(self):
        with open('/proc/meminfo', 'r') as mem:
            ret = {}
            tmp = 0
            for i in mem:
                sline = i.split()
                if str(sline[0]) == 'MemTotal:':
                    ret['total'] = int(sline[1])
                elif str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                    tmp += int(sline[1])
            ret['free'] = tmp
            ret['used'] = int(ret['total']) - int(ret['free'])
        return ret 
