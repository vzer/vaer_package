#!/usr/bin/env python
#coding=utf8
#  use:for web deploy models
__author__ = 'vzer'


import datetime,time
import uuid
from run import db
import hashlib
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash



class ServerInfo(db.Model):
    __tablename__='serverinfo'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    hostname=db.Column(db.String(50))
    ip=db.Column(db.String(50))
    account=db.Column(db.String(50))
    password=db.Column(db.String(50))
    servicename=db.Column(db.String(50))
    environment=db.Column(db.String(50))


class User(db.Model,UserMixin):
    __tablename__='user'
    id=db.Column(db.String(50),primary_key=True,unique=True)
    user_account=db.Column(db.String(50),unique=True)
    user_password=db.Column(db.String(100))
    email=db.Column(db.String(50),unique=True)
    nick_name=db.Column(db.String(50))
    isactive=db.Column(db.Boolean,default=False)
    isadmin=db.Column(db.Boolean,default=False)
    createdate=db.Column(db.DateTime)

    def __init__(self,account=None,password=None,email=None,name=None,isactive=True,isadmin=True,createdate=db.func.now()):
        print "this is my init"
        self.id=createWorkOrder()
        self.user_account=account
        self.email=email
        self.nick_name=name
        self.isactive=isactive
        self.isadmin=isadmin
        self.createdate=createdate
        self.set_password(password=str(password))

    def set_password(self,password):
        self.user_password=generate_password_hash(password=password)

    def check_password(self,password):
        return check_password_hash(self.user_password,password=password)


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


    def __repr__(self):
        return "<User '{:s}'> ".format(self.nick_name)

class Permission_Group(db.Model):
    __tablename__='permission_group'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    group_name=db.Column(db.String(50),unique=True)

class TaskLogs(db.Model):
    __tablename__='tasklog'
    id=db.Column(db.String(50),primary_key=True,unique=True)
    user_id=db.Column(db.String(50))
    deploytype=db.Column(db.String(50))
    family=db.Column(db.String(50))
    models=db.Column(db.String(50))
    version=db.Column(db.String(50))
    status=db.Column(db.String(50))
    failure_times=db.Column(db.Integer)
    logtime=db.Column(db.DateTime)
    context=db.Column(db.Text)

    def __init__(self,id,user_id,deploytype,family,models,version,status,failure_time,context):
        self.id=id
        self.user_id=user_id
        self.deploytype=deploytype
        self.family=family
        self.models=models
        self.version=version
        self.status=status
        self.failure_times=failure_time
        self.logtime=db.func.now()
        self.context=context


class DeployType(db.Model):
    __tablename__='deploytype'
    type_id=db.Column(db.String(50),primary_key=True,unique=True)
    type_name=db.Column(db.String(50),unique=True)

class Models(db.Model):
    __tablename__='models'
    model_id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    type_id=db.Column(db.String(50))
    deploy_type=db.Column(db.String(50))
    type_name=db.Column(db.String(50))
    mode_name=db.Column(db.String(50))
    mode_pet=db.Column(db.String(50),unique=True)
    remote_path=db.Column(db.String(50))
    git_url=db.Column(db.String(50))

    def __init__(self,type_id='',deploy_type='',type_name='',mode_name='',mode_pet='',remote_path='',git_url=''):
        self.type_id=type_id
        self.deploy_type=deploy_type
        self.type_name=type_name
        self.mode_name=mode_name
        self.mode_pet=mode_pet
        self.remote_path=remote_path
        self.git_url=git_url

class DeployOrder(db.Model):
    __tablename__="deployorder"
    order_id=db.Column(db.Integer,primary_key=True,unique=True)

class DeployEnv(db.Model):
    __tablename__="deployenv"
    env_id=db.Column(db.Integer,primary_key=True,unique=True)
    env_name=db.Column(db.String(50),unique=True)
    env_tip=db.Column(db.String(200))
    create_time=db.Column(db.DateTime)

    def __init__(self,name,tip):
        self.env_id=time.mktime(datetime.datetime.now().timetuple())
        self.env_name=name
        self.env_tip=tip
        self.create_time=db.fun.now()


######################################################################################################################
#订单生成器
def createWorkOrder():
    try:
        workOrder=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return uuid.uuid3(uuid.NAMESPACE_DNS,workOrder)
    except Exception,msg:
        print str(msg)
#######################################################################################################################
#时间处理
def dodatetime(date):
    print date.strftime("%Y-%m-%d")
    return date.strftime("%Y-%m-%d")
#######################################################################################################################
if __name__ == '__main__':
    db.create_all()