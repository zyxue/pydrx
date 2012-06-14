#!/usr/bin/env python

import os
import time
import socket
import logging
import threading
import subprocess

import yaml
import flask
import requests
import sqlalchemy
from sqlalchemy import orm

import db_tables as dbtb

class Node(object):
    def __init__(self, **kwargs):
        self.pbs_jobid = os.getenv('PBS_JOBID', 'zyxue_JOBID')
        self.pbs_jobname = os.getenv('PBS_JOBNAME', 'zyxue_JOBNAME')
        self.pbs_num_nodes = os.getenv('PBS_NUM_NODES', 'zyxue_NUM_NODES')
        self.pbs_queue = os.getenv('PBS_QUEUE', 'zyxue_QUEUE') # batch_eth, batch_ib, debug
        self.pbs_o_workdir = os.getenv('PBS_O_WORKDIR', 'zyxue_O_WORKDIR')
        self.pbs_momport = os.getenv('PBS_MOMPORT', 'zyxue_MOMPORT')
        self.pbs_environment = os.getenv('PBS_ENVIRONMENT', 'zyxue_ENVIRONMENT') # e.g. PBS_INTERACTIVE
        self.hostname = os.getenv('HOSTNAME', 'zyxue_HOSTNAME')
        self.bigmaster_flag = os.getenv('BIGMASTER_FLAG')

        try:
            self.yamlf = os.environ["YAML"]
        except KeyError:
            print "YAML env not found, serious problem!"        

        rootdir = os.path.dirname(os.path.abspath(self.yamlf))
        params = yaml.load(open(self.yamlf))
        self.db = os.path.join(rootdir, params.get('database'))
        self.topology = os.path.join(rootdir, params.get('topology'))
        self.hostfile = os.path.join(rootdir, params.get('hostfile'))
        self.logfile = os.path.join(rootdir, params.get('logfile'))
        self.DEBUG=params['DEBUG']

        # sysname = params['sysname']
        # rootdir = params['rootdir']
        # misc_params = params['MISC']
        # system = System(sysname, rootdir, misc_params)
        if self.DEBUG:
            self.ip_addr = "127.0.0.1"
        else:
            self.ip_addr = socket.gethostbyname(socket.gethostname())
        self.port = int(kwargs.get("port", 1234))                # can be configured

        self.start_time = time.time()
        self.walltime = int(params['walltime']) * 60        # in seconds
        self.estimated_end_time = self.start_time + self.walltime
        self.timeout = int(params['timeout']) * 60          # in seconds
        
    def __repr__(self):
        # this is the same as that for dbtb.YoungNode
        return "<YoungNode {0} started at {1} ({2}:{3})>".format(
            self.hostname, 
            time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(self.start_time)),
            self.ip_addr, self.port)

class Master(Node):
    def __init__(self, **kwargs):
        super(Master, self).__init__(**kwargs)
        # logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s', filename=self.logfile)
        if self.DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def init_db(self):
        engine = sqlalchemy.create_engine('sqlite:///{0}'.format(self.db), echo=self.DEBUG)
        dbtb.YoungNode.metadata.create_all(engine)          # CREATE TABLE
        S = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False)
        return S

    def connect_db(self):
        S = self.init_db()                    # init db
        return S()                            # create a new session

    def broadcast_url(self):
        """write 'ip:port' to a hostfile"""
        with open(self.hostfile, 'w') as opf:
            opf.write("http://{0}:{1}\n".format(self.ip_addr, self.port))

    def get_the_youngest_node(self):
        session = self.connect_db()
        n = session.query(dbtb.YoungNode).order_by("start_time desc").first()
        logging.info("YOUNGEST NODE FOUND: {0} for {1})".format(n, self.__repr__()))
        return n

    def invite_switch(self):
        n = self.get_the_youngest_node()
        url = "{0}:{1}".format(n.ip_addr, n.port)
        r = requests.post("http://{0}/invite_switch".format(url), data={"n":repr(n)})
        reply = r.text
        return reply

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

        @app.route('/imyoung', methods=["POST"])
        def store_imyoung():
            session = self.connect_db()
            ynode = dbtb.YoungNode(hostname=flask.request.form['hostname'],
                                   start_time=flask.request.form['start_time'],
                                   ip_addr=flask.request.form['ip_addr'],
                                   port=int(flask.request.form['port']))
            session.add(ynode)
            session.commit()
            message = "YoungNode RECORDED: {0}".format(ynode)
            logging.info(message)
            return message

        @app.route('/get_cmd', methods=["GET"])
        def dispatch_cmd():
            return "date >> lala; pwd >> lala; sleep 10"
            # what should I do here? probably consult the conf file, how to
            # construct the mpirun command?

        @app.route('/report', methods=["POST"])
        def reply_to_report():
            # Process the report (basically a list of files with absolute paths
            # from the slaves), do some necessary db IO, exchange should happen
            # here.
            return "report received"

        @app.route('/request_switch', methods=["GET"])
        def reply_to_request():
            message = "REQUEST RECEIVED"
            logging.info("{0} from bigslave ({1})".format(
                    message, flask.request.headers.get("Host")))
            self.invite_switch()
            # t = threading.Thread(target=self.invite_switch)
            # t.start()
            return message

        @app.route('/invite_switch', methods=["POST"])
        def reply_to_invitation():
            """
            This request must come from the big master on another node,
            i.e. I am not the big master when receiving this request
            """ 
            n = flask.request.form['n']
            logging.info("INVITATION RECEIVED for switch from {0} at {1}".format(
                    n, self.__repr__()))

            self.broadcast_url()

            message = "SWITCH FINISHED"
            logging.info('{0}: From {1} To {2}'.format(
                    message, n, self.__repr__()))
            return message

        if self.DEBUG:
            app.run(host="127.0.0.1", port=int(self.port), debug=True)
        else:
            app.run(host="0.0.0.0", port=int(self.port), debug=False)

class Slave(Node):
    """
    Slave is stupid, it doesn't do much (absolutely no analysis or IOing
    database) other than run the command received from Master, and report to
    the master when finished, then such cycle repeated until it dies
    """
    def say_imyoung(self, uri=None):
        url = uri if uri else self.get_url()
        params = {'hostname': self.hostname,
                  'start_time': self.start_time,
                  'ip_addr': self.ip_addr,
                  'port': self.port,}
        r = requests.post("{0}/imyoung".format(url), data=params)
        return r.text

    def get_url(self):
        with open(self.hostfile) as f:
            url = f.readline().strip()
        return url

    def get_cmd(self):
        url = self.get_url()
        r = requests.get("{0}/get_cmd".format(url))
        return r.text                                       # needed to be tested

    def run(self, cmd):
        returncode = subprocess.call(cmd, shell=True)
        return returncode

    def report(self, cmd):
        report_params = self.gen_report(cmd)
        url = self.get_url()
        r = requests.post("{0}/report".format(url), data=report_params)
        reply = r.text                             # could be "report received"
        return r.text

    def gen_report(self, cmd):
        # e.g. xtc, tpr, edr, log, parsing is based on the cmd
        return {"xtc": "lala.xtc",
                "tpr": "lala.tpr",
                "edr": "lala.edr",
                "log": "lala.log",
                }

    def request_switch(self):
        """
        request the big master on the same node with this slave to invite
        another node for switch
        """
        url = self.get_url()
        r = requests.get("{0}/request_switch".format(url))
        return r.text

# class System(object):
#     def __init__(self, sysname, rootdir, params):
#         self.rootdir = rootdir                              # required
#         self.sysname = sysname                              # required

#         fp = self.fullpath
#         _top = params['topology']
#         self.topf = fp(_top) if _top else fp('{0}.top'.format(self.sysname))
#         _db  = params['database']
#         self.dbf  = fp(_db) if _db else fp('{0}.db'.format(self.sysname))

#     def fullpath(self, f):
#         return os.path.join(self.rootdir, f)
        
#     def __repr__(self):
#         return "<{0} at {1} top: {2} db: {3}>".format(
#             self.sysname, self.rootdir, self.topf, self.dbf)
