#!/usr/bin/env python

import os
import time
import socket

import sqlalchemy

DEBUG=True

class Node(object):
    def __init__(self):
        self.pbs_jobid = os.getenv('PBS_JOBID', 'zyxue_JOBID')
        self.pbs_jobname = os.getenv('PBS_JOBNAME', 'zyxue_JOBNAME')
        self.pbs_num_nodes = os.getenv('PBS_NUM_NODES', 'zyxue_NUM_NODES')
        self.pbs_queue = os.getenv('PBS_QUEUE', 'zyxue_QUEUE') # batch_eth, batch_ib, debug
        self.pbs_o_workdir = os.getenv('PBS_O_WORKDIR', 'zyxue_O_WORKDIR')
        self.pbs_momport = os.getenv('PBS_MOMPORT', 'zyxue_MOMPORT')
        self.pbs_environment = os.getenv('PBS_ENVIRONMENT', 'zyxue_ENVIRONMENT') # e.g. PBS_INTERACTIVE
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = '999'                                  # can be configured
        
        self.start_time = time.time()
        self.walltime = 2 * 60 * 60                         # in seconds
        self.estimated_end_time = self.start_time + self.walltime

class Master(Node):
    def init_db(self, db):
        engine = sqlalchemy.create_engine('sqlite:///{0}'.format(db), echo=DEBUG)
        return engine

    def connect_db(self, db):
        engine = self.init_db(db)
        sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=True, autocommit=False)
        return sessionmaker

    def introduce_myself(self):
        
        return self.estimated_end_time

    def read_db(self):
        pass

    def write_db(self, session, item_row):
        session.write(item_row)

    def broadcase_url(self):
        # write ip:port to a __HOSTNAME__.txt
        pass

    def arouse_slaves(self):
        # arouse the number of slaves according to the configuration files
        pass

    def dispatch_cmd(self):
        """send the slave something like mpirun -np blahblah..."""
        pass

    def receive_report(self):
        # Process the report (basically a list of files with absolute paths
        # from the slaves
        pass

    def switch(self):
        """when the estimated_end_time is very close, Master will find the
        youngest slave and talk about inheritance"""
        pass

    def exchange(self):
        """
        the code here dependes on what exchange you want to do
        e.g. calc_drpe(self) if using STDR

        """
        pass

class Slave(Node):
    """
    Slave is stupid, it doesn't do much (absolutely no analysis or IOing
    database) other than run the command received from Master, and report to
    the master when finished, then such cycle repeated until it dies
    """
    def connect_master(self):
        pass

    def get_cmd(self):
        pass

    def run_cmd(self):
        pass

    def repot(self):
        """report a list of files with absolute paths"""
        pass
