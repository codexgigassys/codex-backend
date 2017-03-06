#!/usr/bin/env python
# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
#
# In the unfortunate case that a worker is forcefully
# stopped while having the semaphore, all workers
# will lock. The chance of this happening is low
# but can happen (and has happened).
# Here is the code to release the semaphore.
#
import pathmagic
from redis import Redis
from redis_semaphore import Semaphore
from threading import Thread
from db_pool import *


semaphore = Semaphore(Redis(host=envget('redis.host')),
                      count=1, namespace='example')
token = semaphore.get_namespaced_key('example')
semaphore.signal(token)
