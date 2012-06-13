#! /usr/bin/env python

import os
import time
import threading

import yaml

from obj import Master, Slave, System

# get configuration from YAML env
try:
    yamlf = os.environ("YAML")
except KeyError:
    print "YAML env not found, serious problem!"

params = yaml.load(open(yamlf))
sysname = params['sysname']
rootdir = params['rootdir']
misc_params = params['MISC']
system = System(sysname, rootdir, misc_params)

##################################MASTER PART##################################
master = Master()

# say_imyoung should be the first thing to do
master.say_imyoung(system.db)  

if master.big_master_flag:
    master.broadcast_url()
else:
    time.sleep(10)                   # give the master 10s to broadcast its url

thread = threading.Thread(target=master.wakeup)

##################################SLAVE PART###################################
slave = Slave()
hostfile="__HOSTNAME__.txt"

while True:
    cmd = slave.get_cmd(hostfile)
    slave.run(cmd)
    slave.report(cmd)
    # if less than 30 min is left, too old
    if slave.estimated_end_time - time.time() < (30 * 60):
        if slave.big_master_flag:
            r = slave.request_switch(hostfile)
            if r == "Done":                # meaning the swithing has succeeded
                break
        else:
            break
