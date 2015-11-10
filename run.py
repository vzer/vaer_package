#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from flask import Flask
from flask_login import LoginManager
from development import Development
from flask.ext.sqlalchemy import SQLAlchemy
import multiprocessing as mp
from plugin import pack
from development import cntl_q,data_q

app=Flask(__name__)
lm=LoginManager()
lm.init_app(app)
lm.login_view="login"
lm.login_message="此操作未授权，请登录系统。"
app.config.from_object(Development)
db=SQLAlchemy(app)

from adminview import *
from views import *


if __name__ == '__main__':
    p=mp.Process(target=pack.main,args=(cntl_q,data_q))
    p.start()
    app.run(host="0.0.0.0",port=8080)