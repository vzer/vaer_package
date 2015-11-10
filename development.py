#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

import multiprocessing
import default

#for pack multiprocess
cntl_q=multiprocessing.Queue()
data_q=multiprocessing.Queue()

POST_PRE_PAGE=25

class Development(default.Config):
    #app.config
    DEBUG=True
    CSRF_ENABLED = True
    SECRET_KEY="xiniunet-delpoy"
    POST_PRE_PAGE=8

    #mysql config
    MYSQL_DB = "deploy"
    MYSQL_USER = "vzer"
    MYSQL_PASS = "wwwlin123"
    MYSQL_HOST = "192.168.1.246"
    MYSQL_PORT = int("3306")

    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' \
                          % (MYSQL_USER, MYSQL_PASS,
                             MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
    SQLALCHEMY_ECHO=True