#! /usr/bin/env python

import time
import fcntl
# import portalocker
# with portalocker.Lock('/tmp/locktest', timeout=1) as fh:
#     print >>fh, 'writing some stuff to my cache...'

f = open('/tmp/locktest', 'w')
# fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
# time.sleep(5)
f.write("{0}\n".format(__file__))
f.close()
