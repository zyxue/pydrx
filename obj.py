#!/usr/bin/env python

import os
import time
import socket
import logging
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
        self.bigmaster_flag = os.getenv('BIGMASTER_FLAG')
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

    def write_db(self, session, item_row):
        session.add(item_row)

    def say_i_am_young(self, db):
        session = self.connect_db(db)
        ynode = dbtb.YoungNode(hostname=self.hostname,
                               start_time=self.start_time,
                               ip_address=self.ip_address)
        self.write_db(session, ynode)
        session.commit()
        return self.estimated_end_time

    def broadcast_url(self, hostfile="__HOSTNAME__.txt"):
        """write 'ip:port' to a __HOSTNAME__.txt"""
        if not os.path.exists(hostfile):
            with open(hostfile, 'w') as opf:
                opf.write("http://{0}:{1}\n".format(self.ip_address, self.port))

    def get_the_youngest_url(self):
        # session = self.connect_db(db)
        # session.query(YoungNode).
        pass

    def invite_switch(self):
        url = self.get_the_youngest_url()
        r = requests.post("http://{0}/invite_switch".format(url))
        if r.text == url:
            logging.info('bigmaster switched from {0} to {1}'.format(self.ip_address, url))

    def wakeup(self):
        app = flask.Flask(__name__)

        @app.before_request
        def before_request():
            # Just store whatever you want on flask.g
            flask.g.session = self.connect_db()

        @app.teardown_request
        def teardown_request(exception):
            if hasattr(flask.g, 'session'):
                flask.g.session.commit()

        @app.route('/get_cmd', methods=["GET"])
        def dispatch_cmd():
            # what should I do here? probably consult the conf file, how to
            # construct the mpirun command?
            pass

        @app.route('/report', methods=["POST"])
        def receive_report():
            # Process the report (basically a list of files with absolute paths
            # from the slaves), do some necessary db IO, exchange should happen
            # here.
            pass

        @app.route('/request_switch', methods=["GET"])
        def reply_to_switch(self):
            """This message must come from the slave which is on the same node"""
            self.invite_switch()
            return "done"

        @app.route('/invite_switch', methods=["GET"])
        def reply_to_switch(self):
            """
            This request must come from the big master on another node,
            i.e. I am not the big master when receiving this request
            """ 
            # maybe the new url should be broadcasted by the old server? not sure
            self.broadcast_url(hostfile="__HOSTNAME__.txt")
            return self.ip_address

        app.run()

class Slave(Node):
    """
    Slave is stupid, it doesn't do much (absolutely no analysis or IOing
    database) other than run the command received from Master, and report to
    the master when finished, then such cycle repeated until it dies
    """
    def get_url(self, hostfile):
        with open(hostfile) as f:
            url = f.readline().strip()
        return url

    def get_cmd(self, hostfile):
        url = self.get_url(hostfile)
        r = requests.get("{0}/get_cmd".format(url))
        return r.text                                       # needed to be tested

    def run(self, cmd):
        returncode = subprocess.call(cmd)
        return returncode

    def report(self, cmd):
        report_params = self.gen_report(cmd)
        url = self.get_url()
        r = requests.post("{0}/report".format(url), data=report_params)
        return r

    def gen_report(self, cmd):
        # e.g. xtc, tpr, edr, log, parsing is based on the cmd
        return {"xtc": "lala.xtc",
                "tpr": "lala.tpr",
                "edr": "lala.edr",
                "log": "lala.log",
                }

    def request_switch(self, hostfile):
        """
        request the big master, which should be on the same node with this
        slave to invite another node for switch
        """
        url = self.get_url(hostfile)
        r = requests.get("{0}/request_switch".format(url))
        return r.text

class System(object):
    def __init__(self, sysname, rootdir, params):
        self.rootdir = rootdir                              # required
        self.sysname = sysname                              # required

        fp = self.fullpath
        _top = params['topology']
        self.topf = fp(_top) if _top else fp('{0}.top'.format(self.sysname))
        _db  = params['database']
        self.dbf  = fp(_db) if _db else fp('{0}.db'.format(self.sysname))

    def fullpath(self, f):
        return os.path.join(self.rootdir, f)
        
    def __repr__(self):
        return "<{0} at {1} top: {2} db: {3}>".format(
            self.sysname, self.rootdir, self.topf, self.dbf)
