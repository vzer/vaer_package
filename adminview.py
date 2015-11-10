#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

from flask import Flask,url_for,request,redirect,g,flash
from flask.ext.login import current_user,login_user,logout_user
from flask_admin import Admin,expose,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from run import app,db
from models import User,Models
from wtforms.validators import required,Email


class UserAdmin(ModelView):
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ["user_account","nick_name"]
    column_filters = ["isactive","isadmin"]
    column_editable_list = ["email","nick_name","isactive","isadmin"]
    column_labels = dict(user_account="登录账户",email="电子邮箱",nick_name="用户姓名",isadmin="管理",isactive="状态",createdate="创建日期",user_password="用户密码")
    form_args = {
        "user_account":{
            "label":"登录账户",
            "validators":[required()]
        },
        "email":{
            "label":"电子邮箱",
            "validators":[required(),Email()]
        },
        "nick_name":{
            "label":"用户名称",
            "validators":[required()]
        },
        "isactive":{
            "label":"是否激活",
            "validators":[required()]
        },
        "isadmin":{
            "label":"是否admin",
            "validators":[required()]
        },
        "createdate":{
            "label":"创建时间",
            "validators":[required()]
        },
        "user_password":{
            "label":"用户密码",
            "validators":[required()]
        },
    }

    def __init__(self,session):
        super(UserAdmin,self).__init__(User,db.session)

    def is_accessible(self):
        return current_user.is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login",next=request.url))

    def create_model(self, form):
        try:
            model=self.model()
            form.populate_obj(model)
            print "this is create_model"
            print model.user_password
            model.set_password(model.user_password)
            print model.user_password
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to create record. %(error)s', error=str(ex))
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)
        return model

    def update_model(self, form, model):
        try:
            form.populate_obj(model)
            print "this is update_model"
            print model.user_password
            if not("pbkdf2:sha1" in model.user_password):
                model.set_password(model.user_password)
            print model.user_password
            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to update record. %(error)s', error=str(ex))

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, False)

        return True





class ModelsAdmin(ModelView):
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_searchable_list = ["mode_pet"]
    column_filters = ["deploy_type"]
    column_exclude_list = ["type_id"]
    column_editable_list = ["remote_path","git_url","mode_name","mode_pet"]
    column_labels = dict(deploy_type="环境",type_name="类别名",mode_name="工程名",mode_pet="打包名",remote_path="上传地址",git_url="gitlab地址")
    form_args = {
        "deploy_type":{
            "label":"环境",
            "validators":[required()]
        },
        "type_name":{
            "label":"类别",
            "validators":[required()]
        },
        "mode_name":{
            "label":"工程名",
            "validators":[required()]
        },
        "mode_pet":{
            "label":"打包名",
            "validators":[required()]
        },
        "remote_path":{
            "label":"上传地址",
            "validators":[required()]
        },
        "git_url":{
            "label":"gitlab地址",
            "validators":[required()]
        },
    }
    def __init__(self,session):
        super(ModelsAdmin,self).__init__(Models,db.session())

    def is_accessible(self):
        return current_user.is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login",next=request.url))



admin=Admin(name="xiniu_admin",template_mode="bootstrap3")
admin.init_app(app)
admin.add_view(UserAdmin(db.session()))
admin.add_view(ModelsAdmin(db.session()))