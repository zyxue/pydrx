#!/usr/bin/env python

import time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class YoungNode(Base):
    __tablename__ = "youngnode"
    
    ID = Column(Integer, primary_key=True)
    hostname = Column(String)
    start_time = Column(Float)
    ip_addr = Column(String)
    port = Column(Integer)

    def __init__(self, hostname, start_time, ip_addr, port):
        self.hostname = hostname
        self.start_time = start_time
        self.ip_addr = ip_addr
        self.port = port

    def __repr__(self):
        return "<YoungNode {0} started at {1} ({2}:{3})>".format(
            self.hostname, 
            time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(self.start_time)),
            self.ip_addr, self.port)
