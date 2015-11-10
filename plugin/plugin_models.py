#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from xml.etree import ElementTree as ET

Base=declarative_base()

class TaskLogs(Base):
    __tablename__='tasklog'
    id=Column(String(50),primary_key=True,unique=True)
    user_id=Column(String(50))
    deploytype=Column(String(50))
    family=Column(String(50))
    models=Column(String(50))
    version=Column(String(50))
    status=Column(String(50))
    failure_times=Column(Integer)
    logtime=Column(DateTime)
    context=Column(Text)

    def __init__(self,id,user_id,deploytype,family,models,version,status,failure_time,context):
        self.id=id
        self.user_id=user_id
        self.deploytype=deploytype
        self.family=family
        self.models=models
        self.version=version
        self.status=status
        self.failure_times=failure_time
        self.logtime=func.now()
        self.context=context

#######################################################################################################################
def resoveXml(xmlpath):
    tree=ET.parse(xmlpath)
    root=tree.getroot()
    for key in root:
        if key.tag=="{http://maven.apache.org/POM/4.0.0}version":
            return str(key.text)