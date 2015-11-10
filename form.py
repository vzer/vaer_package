#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'
from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo

class LoginForm(Form):
    username=StringField("登录账户:",validators=[Length(min=4,max=16)])
    password=PasswordField("登录密码:",validators=[Length(min=8,max=16)])
    remember_me=BooleanField("记住我",default=False)


class RededitForm(Form):
    nick_name=StringField("用户姓名:",validators=[DataRequired()])
    username=StringField("登录账户:",validators=[Length(min=4,max=16,message="登录账户不符合要求，（最小4个字符，最大16个字符）")])
    email=StringField("邮箱地址:",validators=[Email(message="邮箱格式不正确")])
    password=PasswordField("登录密码:",validators=[Length(min=8,max=16,message="登录密码不符合要求，（最小4个字符，最大16个字符）"),EqualTo("confirm",message="两次密码一致")])
    confirm=PasswordField("确认密码：",validators=[Length(min=8,max=16,message="确认密码不符合要求，（最小4个字符，最大16个字符）")])
