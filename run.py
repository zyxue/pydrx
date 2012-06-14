#! /usr/bin/env python

# import os
import time
import threading

from obj import Master, Slave

##################################MASTER PART##################################
# on the master side, hostfile is for broadcasting url
master = Master()

if master.big_master_flag:
    master.broadcast_url()
else:
    time.sleep(10)                   # give the master 10s to broadcast its url

thread = threading.Thread(target=master.wakeup)

##################################SLAVE PART###################################
# on the slave side, hostfile is for contacting
slave = Slave()

# say_imyoung should be the first thing to do
slave.say_imyoung()

while True:
    cmd = slave.get_cmd()
    slave.run(cmd)
    slave.report(cmd)

    # if less than 30 min is left, too old
    if slave.estimated_end_time - time.time() < (30 * 60):
        if slave.big_master_flag:
            r = slave.request_switch()
            if r == "Done":                # meaning the swithing has succeeded
                break
        else:
            break
