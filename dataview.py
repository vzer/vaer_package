#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from run import db
from models import (TaskLogs,User,Models)

class DataWrappers(object):
    def countweekdeploy(self,week):
        weekmodel=db.session.query(TaskLogs.deploytype,TaskLogs.models,db.func.count(TaskLogs.models).label("count")).\
            filter(db.func.yearweek(db.func.date_format(TaskLogs.logtime,"%Y-%m-%d"))==week,TaskLogs.status=="SUCCESS").group_by(TaskLogs.deploytype,TaskLogs.models)
        weektotal=weekmodel.count()
        weeklist=weekmodel.all()
        return (weektotal,weeklist)

    def get_entries_by_page(self, page, par_page,username):
        pages = TaskLogs.query.filter(TaskLogs.user_id==username).order_by(TaskLogs.logtime.desc()).paginate(page, par_page)
        return pages

    def get_entries_by_search(self,page,par_page,username,search):
        pages=TaskLogs.query.filter(TaskLogs.user_id==username,TaskLogs.models.like("%%%s%%"%search)).order_by(TaskLogs.logtime.desc()).paginate(page, par_page)
        return pages

