# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
from redis import Redis
from rq import Queue
import sys
from env import envget
qfail = Queue(sys.argv[1],connection=Redis(host=envget('redis.host')))
qfail.count
qfail.empty()

