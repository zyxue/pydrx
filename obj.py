#!/usr/bin/env python

import os
import time
import socket
import subprocess

import flask
import requests
import sqlalchemy

import db_tables as dbtb

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
        self.hostname = os.getenv('HOSTNAME', 'zyxue_HOSTNAME')
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.port = '999'                                  # can be configured
        
        self.start_time = time.time()
        self.walltime = 2 * 60 * 60                         # in seconds
        self.estimated_end_time = self.start_time + self.walltime

class Master(Node):
    def init_db(self, db):
        engine = sqlalchemy.create_engine('sqlite:///{0}'.format(db), echo=DEBUG)
        sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=True, autocommit=False)
        return sessionmaker

    def connect_db(self, db):
        sessionmaker = self.init_db(db)                  # init db
        return sessionmaker()                            # create a new session

    def say_i_am_young(self):
        session = self.connect_db()
        ynode = dbtb.YoungNode(hostname=self.hostname,
                               start_time=self.start_time,
                               ip_address=self.ip_address)
        self.write_db(session, ynode)
        session.commit()
        return self.estimated_end_time

    def query_db(self, sqlcmd):
        # probably query_db needs to be more specific for individual case
        pass

    def write_db(self, session, item_row):
        # only write a single item to the db
        session.add(item_row)

    def broadcase_url(self, hostfile="__HOSTNAME__.txt"):
        """write 'ip:port' to a __HOSTNAME__.txt"""
        if not os.path.exists(hostfile):
            with open(hostfile, 'w') as opf:
                opf.write("http://{0}:{1}\n".format(self.ip_address, self.port))

    def be_in_charge(self):
        app = flask.Flask(__name__)
        app.config.from_object(__name__)
        app.config.from_envvar('FLASKR_SETTINGS', silent=True)

        # self.active = True
        
        @app.before_request
        def before_request():
            # Just store whatever you want on flask.g
            flask.g.session = self.connect_db()

        @app.teardown_request
        def teardown_request(exception):
            if hasattr(flask.g, 'session'):
                flask.g.session.commit()

        @app.route('/get_cmd', method=["GET"])
        def dispatch_cmd():
            # what should I do here? probably consult the conf file, how to
            # construct the mpirun command?
            pass

    def arouse_slaves(self):
        # arouse the number of slaves according to the configuration files
        # loop through the dirs specified in the conf file and qsub run.py
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
    def get_url(self, hostfile="__HOSTNAME__.txt"):
        with open(hostfile) as f:
            url = f.readline().strip()
        return url

    def connect_master(self):
        # I don't think this function is useful
        pass

    def get_cmd(self):
        url = self.get_url()
        r = requests.get("{0}/get_cmd".format(url))
        return r.text                                       # needed to be tested

    def run_cmd(self):
        cmd = self.get_cmd()
        returncode = subprocess.call(cmd)
        return returncode

    def report(self):
        # using post method?
        """report a list of files with absolute paths"""
        pass
