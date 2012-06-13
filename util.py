#! /usr/bin/env python

import Queue
import logging
import subprocess
import threading

def runit(cmd_list, numthread, ftest):
    """
    Putting each analyzing codes in a queue to use multiple cores
    simutaneously.  The code is the same as runit in g_analyze/init2.py
    2012-01-27
    """
    def worker():
        while True:
            cmd = q.get()
            if ftest:
                print cmd
                returncode = 0
            else:
                logging.info('working on {0:s}'.format(cmd))
                returncode = subprocess.call(cmd, shell=True)
            q.task_done()
            return returncode
            
    q = Queue.Queue()

    for i in range(numthread):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for cmd in cmd_list:
        q.put(cmd)
    
    q.join()
