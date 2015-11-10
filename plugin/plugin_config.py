#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
# create_engine(数据库://用户名:密码(没有密码则为空)@主机名:端口/数据库名',echo =True)
MYSQL_DB = "deploy"
MYSQL_USER = "vzer"
MYSQL_PASS = "wwwlin123"
MYSQL_HOST = "192.168.1.246"
MYSQL_PORT = int("3306")

engine=create_engine(
    'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8'%
    (MYSQL_USER,MYSQL_PASS,MYSQL_HOST,MYSQL_PORT,MYSQL_DB),
    echo=True
)

Session=scoped_session(sessionmaker(bind=engine,autoflush=True))
