#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class YoungNode(Base):
    __tablename__ = "youngnode"
    
    id = Column(Integer, primary_key=True)
    
