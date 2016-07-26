from redis import Redis
from rq import Queue
import sys
qfail = Queue(sys.argv[1],connection=Redis())
qfail.count
qfail.empty()

