#!/usr/bin/env python
#coding=utf8

from flask import Flask,render_template,request,redirect,url_for,session,flash,g,abort
from models import TaskLogs,Models,User,createWorkOrder
from werkzeug.security import generate_password_hash
from run import app,db,lm
from development import cntl_q,data_q
import datetime
from form import LoginForm,RededitForm
from flask_login import login_required,login_user,current_user,logout_user
from dataview import DataWrappers
from development import  POST_PRE_PAGE
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

date = DataWrappers()

@app.before_request
def before_request():
    g.user=current_user

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    totlelogs=TaskLogs.query.count()
    todaylogs=TaskLogs.query.filter(db.func.to_days(TaskLogs.logtime)==db.func.to_days(db.func.now()))
    todaylogscount=todaylogs.count()
    todaylogslist=todaylogs.all()
    return render_template("index.html",totlelogs=totlelogs,todaylogscount=todaylogscount,todaylogslist=todaylogslist)

@app.route(("/view/"))
@app.route("/view/<workOrder>")
@login_required
def viewWorkOrder(workOrder=None):
    if workOrder==None:
        logList=None
    else:
        logList=TaskLogs.query.filter_by(id=workOrder).first()
    return render_template("show-wordorder.html",logList=logList)

@app.route("/add/",methods=['GET', 'POST'])
@app.route("/add/<deployType>",methods=['GET', 'POST'])
@login_required
def add(deployType="ALL"):
    workOrder=createWorkOrder()
    if request.method=="GET":
        if deployType=="ALL":
            modelMap=Models.query.order_by(Models.model_id.desc()).all()
        else:
            modelMap=Models.query.filter_by(deploy_type=deployType).order_by(Models.mode_pet.desc()).all()
        return render_template("add.html",deployType=deployType,workorder=workOrder,modelmap=modelMap)
    elif request.method=="POST":
        modelPet=request.form["models"]
        versionNumber=request.form["version_number"]
        sql_list=Models.query.filter_by(mode_pet=modelPet).first()
        modelName=sql_list.mode_name
        typeName=sql_list.type_name
        remote_path=sql_list.remote_path
        git_url=sql_list.git_url
        cntl_q.put({'event':'data'})
        data_q.put({'workOrder':workOrder,'typename':typeName,'modelname':modelName,'versionnumber':versionNumber,'remote_path':remote_path,'git_url':git_url[7:],"user_account":g.user.user_account,"deployType":deployType})
        flash('发布%s模块任务，添加成功！！'%modelName)
        return redirect(url_for("add",deployType=deployType))


@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm()
    if g.user.is_authenticated():
        return redirect(url_for("index"))
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user=User.query.filter_by(user_account=username).first()
        if user is not None and user.check_password(password=password):
            login_user(user,remember=form.remember_me.data)
            flash('hi,%s 你已经登录成功。'%current_user.nick_name)
            next=request.args.get("next")
            return redirect(next or url_for("index"))
        else:
            flash("用户名或密码错误")
    return render_template("login.html",form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('再见,欢迎下次使用。')
    return redirect(url_for("index"))


@app.route("/regedit/",methods=["GET","POST"])
def regedit():
    form=RededitForm(request.form)
    if request.method=="POST" and form.validate():
        nickname=form.nick_name.data
        username=form.username.data
        email=form.email.data
        password=form.password.data
        confirm=form.confirm.data
        user=User(user_account=username,user_password=password,email=email,nick_name=nickname)
        db.session.add(user)
        db.session.commit()
        flash("用户注册成功,请登录。")
        return redirect(url_for("login"))
    else:
        return render_template("regedit.html",form=form)

@app.route("/statis/")
def statis():
    thisweek=db.func.yearweek(db.func.now())
    lastweek=thisweek-1
    (thisweektotal,thisweeklist)=date.countweekdeploy(thisweek)
    (lastweektotal,lastweeklist)=date.countweekdeploy(lastweek)
    print thisweektotal,lastweektotal
    #stmt=db.session.query(TaskLogs.deploytype.label("deploytype"),TaskLogs.models.label("models"),db.func.max(TaskLogs.logtime).label("logtime")).group_by(TaskLogs.deploytype,TaskLogs.models).subquery()
    #current_version=db.session.query(TaskLogs.deploytype,TaskLogs.family,TaskLogs.models,TaskLogs.version,TaskLogs.logtime).join(stmt,TaskLogs.deploytype==stmt.deploytype,TaskLogs.models==stmt.models,TaskLogs.logtime==stmt.logtime).filter(TaskLogs.status=="SUCCESS").order_by(TaskLogs.logtime).all()
    current_version=db.session.execute("""SELECT A.deploytype,A.family,A.models,A.version,A.logtime FROM tasklog AS A INNER JOIN(
	SELECT deploytype as deploytype,models as models,MAX(logtime) AS logtime FROM tasklog GROUP BY deploytype,models
) as B
on A.deploytype=B.deploytype and A.models=B.models AND A.logtime=B.logtime
WHERE `status`='SUCCESS' ORDER BY logtime desc""")
    current_datetime=datetime.datetime.now()
    return render_template("statistics.html",thisweektotal=thisweektotal,thisweeklist=thisweeklist,lastweektotal=lastweektotal,lastweeklist=lastweeklist,current_datetime=current_datetime,current_version=current_version)


@app.route("/show_worklist/",methods=["GET","POST"])
@app.route("/show_worklist/<int:page>",methods=["GET","POST"])
@app.route("/show_worklist/<searchname>/<int:page>",methods=["GET","POST"])
@login_required
def show_worklist(searchname=None,page=1):
    if request.method=="GET":
        if searchname==None:
            if page < 1:
                page = 1
            p = date.get_entries_by_page(page=page, par_page=POST_PRE_PAGE,username=g.user.user_account)
            entries = p.items
            #页数标签
            if not p.total:
                pagination = [0]
            elif p.total % POST_PRE_PAGE != 0:
                pagination = range(1, p.total/POST_PRE_PAGE + 2)
            else:
                pagination = range(1, p.total/POST_PRE_PAGE + 1)

            return render_template('show_worklist.html', entries=entries,
                                   p=p, page=page,searchname=searchname,pagination=pagination)
        else:
            if page < 1:
                page = 1
            p = date.get_entries_by_search(page=page, par_page=POST_PRE_PAGE,username=g.user.user_account,search=searchname)
            entries = p.items
            #页数标签
            if not p.total:
                pagination = [0]
            elif p.total % POST_PRE_PAGE != 0:
                pagination = range(1, p.total/POST_PRE_PAGE + 2)
            else:
                pagination = range(1, p.total/POST_PRE_PAGE + 1)

            return render_template('show_worklist.html', entries=entries,
                                   p=p, page=page,searchname=searchname, pagination=pagination)
    elif request.method=="POST":
        searchname=request.form["searchname"]
        p = date.get_entries_by_search(page=page, par_page=POST_PRE_PAGE,username=g.user.user_account,search=searchname)
        entries = p.items
        #页数标签
        if not p.total:
            pagination = [0]
        elif p.total % POST_PRE_PAGE != 0:
            pagination = range(1, p.total/POST_PRE_PAGE + 2)
        else:
            pagination = range(1, p.total/POST_PRE_PAGE + 1)

        return render_template('show_worklist.html', entries=entries,
                               p=p, page=page,searchname=searchname,pagination=pagination)


