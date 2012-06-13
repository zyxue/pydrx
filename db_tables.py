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
    ip_address = Column(String)

    def __init__(self, hostname, start_time, ip_address):
        self.hostname = hostname
        self.start_time = start_time
        self.ip_address = ip_address

    def __repr__(self):
        return "<YoungNode {0} started at {1} ({2})>".format(
            self.hostname, 
            time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(self.start_time)),
            self.ip_address)
