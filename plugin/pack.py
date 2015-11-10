#!/usr/bin/env python
#coding=utf8
#  use:for web deploy
__author__ = 'vzer'

try:
    from pexpect import pxssh
    import paramiko
except ImportError,msg:
    print(u'本地环境，无此模块！')
import os
import subprocess
import multiprocessing as mp
import time
import socket
from plugin_models import TaskLogs,resoveXml
from plugin_config import Session
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
######################################################################################################################


#shell命令封装
def shellCmd(cmd):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (processStdout,processStderr) = process.communicate()
    #print "W"*20
    #print processStdout
    #print "W"*20
    return (process.returncode,processStdout)
#远程ssh 命令封装
def pxsshWork(hostname,username,password,cmd):
    try:
        sshClient=pxssh.pxssh()
        sshClient.login (hostname, username, password, original_prompt='[$#>]')
        sshClient.sendline (cmd)
        sshClient.prompt()
        result=sshClient.before
        sshClient.logout()
        return (True,result)
    except pxssh.ExceptionPxssh,msg:
        print('login failed')
        return (False,str(msg))
logText=''
#日志收集器
def logCollector(info):
    global logText
    try:
        logText=logText+info+'\r\n'
    except Exception,msg:
        logText=logText+str(msg)+'\r\n'


#采用 paramiko 上传文件
def putFileWork(accout,passwd,host,localPath,remotePath,filename):
    try:
        remoteHost=(host,22)
        remoteClient=paramiko.Transport(remoteHost)
        remoteClient.connect(username=accout,password=passwd)
        sshFtp=paramiko.SFTPClient.from_transport(remoteClient)
        logCollector('-'*80)
        logCollector('开始上传文件 %s '%datetime.datetime.now())
        sshFtp.put(localPath+filename,remotePath+filename)
        logCollector('上传成功 %s '%datetime.datetime.now())
        logCollector('#'*80)
        remoteClient.close()
        return True
    except paramiko.AuthenticationException,msg:
        logCollector(str(msg))
        return False
    except socket.error,msg:
        logCollector(str(msg))
        return False
    except IOError,msg:
        logCollector(str(msg))
        return False

#Service 服务打包
def deployServiceWork(username,passwd,localServicePath,remoteTarPath,version,host,projectName,git_url):
    failureTimes=0
    try:
        logCollector('#'*30+'部署任务开始'+'#'*30)
        #删除遗留的项目文件夹，并判断删除结果
        logCollector('#'*20+'step 1：删除上次遗留的'+projectName+' 项目'+'#'*20)
        rmDirCmd='rm -rf %s/%s' %(localServicePath,projectName)
        (recode,result)=shellCmd(rmDirCmd)
        logCollector(result)
        if recode==0:
            logCollector('.'*20+'SUCCESS！！：DELETE THE OLD '+'.'*20)
            logCollector('#'*20+'step 2:git 克隆'+projectName+'项目包到本地'+'#'*20)
            #从gitlab把项目的工程打包下来，并判断打包是否成功
            gitCloneCmd='git clone -b %s http://readonly:readonly@%s %s/%s'%(version,git_url,localServicePath,projectName)
            (recode,result)=shellCmd(gitCloneCmd)
            logCollector(result)
            if recode==0:
                logCollector('.'*20+'SUCCESS！！： GIT CLONE THE MODELS'+'.'*20)
                #判断pom.xml文件 发布版本是否存在snatshot release 版本字样
                versionTag=resoveXml("%s/%s/%s-business/pom.xml"%(localServicePath,projectName,projectName))
                if not ("SNAPSHOT" in versionTag.upper() or "RELEASE" in versionTag.upper()):
                    if version==versionTag:
                        logCollector('#'*20+'setp 3:maven '+projectName+' contract 组件'+'#'*20)
                        #进入项目的contract目录下先清理后deploy，并判断是否成功
                        inFounfationContractCmd='%s/%s/%s-contract'%(localServicePath,projectName,projectName)
                        os.chdir(inFounfationContractCmd)
                        mvnCleanCmd='mvn clean deploy'
                        (recode,result)=shellCmd(mvnCleanCmd)
                        logCollector(result)
                        if recode==0:
                            logCollector('.'*20+'SUCCESS！！：MVN CLEAN DEPLOY'+'.'*20)
                        else:
                            logCollector('.'*20+'FAILURE！！：MVN CLEAN DEPLOY'+'.'*20)
                            failureTimes=failureTimes+1
                        #进入项目的business目录下，打包项目，并判断是否成功
                        logCollector('#'*20+'setp 4:maven '+projectName+' business 组件'+'#'*20)
                        inFounfationBusinessCmd='../../../%s/%s/%s-business'%(localServicePath,projectName,projectName)
                        os.chdir(inFounfationBusinessCmd)
                        mvnInstallCmd='mvn clean install -Dmaven.test.skip=true -U'
                        (recode,result)=shellCmd(mvnInstallCmd)
                        logCollector(result)
                        if recode==0:
                            logCollector('.'*20+'SUCCESS！！：MVN CLEAN INSTALL'+'.'*20)
                            logCollector('#'*20+'step 5:上传'+projectName+'部署包到远端服务器'+'#'*20)
                            localPath='target/'
                            tarFilename='%s-business-%s-assembly.tar.gz' %(projectName,version)
                            shellStatus=putFileWork(accout=username,passwd=passwd,host=host,localPath=localPath,remotePath=remoteTarPath,filename=tarFilename)
                            if shellStatus:
                                logCollector('.'*20+'SUCCESS！！：UPLOAD THE TAR PACKAGE'+'.'*20)
                                return (0,failureTimes)
                            else:
                                logCollector('.'*20+'FAILURE！！：UPLOAD THE TAR PACKAGE'+'.'*20)
                                failureTimes=failureTimes+1
                                return (1,failureTimes)
                        else:
                            logCollector('.'*20+'FAILURE！！：MVN CLEAN INSTALL'+'.'*20)
                            failureTimes=failureTimes+1
                            return (1,failureTimes)
                    else:
                        logCollector('.'*20+'FAILURE！！：THE DEPLOY VERSION:%s != THE POM.xml VERSION:%s '%(version,versionTag)+'.'*20)
                        failureTimes=failureTimes+1
                        return (1,failureTimes)
                else:
                    logCollector('.'*20+'FAILURE！！：PLEASE CHECK THE POM.xml FILE(have the %s) '%versionTag+'.'*20)
                    failureTimes=failureTimes+1
                    return (1,failureTimes)
            else:
                logCollector('.'*20+'FAILURE！！： GIT CLONE THE MODELS'+'.'*20)
                failureTimes=failureTimes+1
                return (1,failureTimes)
        else:
            logCollector('.'*20+'FAILURE！！：DELETE THE OLD '+'.'*20)
            failureTimes=failureTimes+1
            return (1,failureTimes)
    except subprocess.CalledProcessError,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)
    except OSError,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)
    except Exception,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)

#Web 服务打包
def deployWebWork(username,passwd,localServicePath,remoteTarPath,version,host,projectName,git_url):
    failureTimes=0
    try:
        logCollector('#'*30+'部署任务开始'+'#'*30)
        #删除遗留的项目文件夹，并判断删除结果
        logCollector('#'*20+'step 1：删除上次遗留的'+projectName+' 项目'+'#'*20)
        rmDirCmd='rm -rf %s/%s' %(localServicePath,projectName)
        (recode,result)=shellCmd(rmDirCmd)
        logCollector(result)
        #如果删除ok，开始git 工程包到本地
        if recode==0:
            logCollector('.'*20+'SUCCESS！！：DELETE THE OLD '+'.'*20)
            logCollector('#'*20+'step 2:git 克隆'+projectName+'项目包到本地'+'#'*20)
            gitCloneCmd='git clone -b %s http://readonly:readonly@%s %s/%s'%(version,git_url,localServicePath,projectName)            #print gitCloneCmd
            (recode,result)=shellCmd(gitCloneCmd)
            logCollector(result)
            #如果git ok，进入到 项目目录，判断pom文件时候符合要求，
            if recode==0:
                logCollector('.'*20+'SUCCESS！！： GIT CLONE THE MODELS'+'.'*20)
                logCollector('#'*20+'setp 3:maven '+projectName+'组件'+'#'*20)
                inFounfationBusinessCmd='%s/%s/'%(localServicePath,projectName)
                os.chdir(inFounfationBusinessCmd)
                versionTag=resoveXml("pom.xml")
                #如果pom文件符合要求，开始maven
                if not ("SNAPSHOT" in versionTag.upper() or "RELEASE" in versionTag.upper()):
                    if versionTag==version:
                        mvnInstallCmd='mvn clean install -Dmaven.test.skip=true -U'
                        (recode,result)=shellCmd(mvnInstallCmd)
                        logCollector(result)
                        #如果maven成功，开始上传到远程服务器
                        if recode==0:
                            logCollector('.'*20+'SUCCESS！！：MVN CLEAN INSTALL'+'.'*20)
                            logCollector('#'*20+'step 5:上传'+projectName+'部署包到远端服务器'+'#'*20)
                            localPath='target/'
                            tarFilename='%s-%s.war'%(projectName,version)
                            shellStatus=putFileWork(accout=username,passwd=passwd,host=host,localPath=localPath,remotePath=remoteTarPath,filename=tarFilename)
                            if shellStatus:
                                logCollector('.'*20+'SUCCESS！！：UPLOAD THE TAR PACKAGE'+'.'*20)
                                return (0,failureTimes)
                            else:
                                logCollector('.'*20+'FAILURE！！：UPLOAD THE TAR PACKAGE'+'.'*20)
                                failureTimes=failureTimes+1
                                return (1,failureTimes)
                        else:
                            logCollector('.'*20+'FAILURE！！：MVN CLEAN INSTALL'+'.'*20)
                            failureTimes=failureTimes+1
                            return (1,failureTimes)
                    else:
                        logCollector('.'*20+'FAILURE！！：THE DEPLOY VERSION:%s != THE POM.xml VERSION:%s '%(version,versionTag)+'.'*20)
                        failureTimes=failureTimes+1
                        return (1,failureTimes)
                else:
                    logCollector('.'*20+'FAILURE！！：PLEASE CHECK THE POM.xml FILE(have the %s) '%versionTag+'.'*20)
                    failureTimes=failureTimes+1
                    return (1,failureTimes)
            else:
                logCollector('.'*20+'FAILURE！！： GIT CLONE THE MODELS'+'.'*20)
                failureTimes=failureTimes+1
                return (1,failureTimes)
        else:
            logCollector('.'*20+'FAILURE！！：DELETE THE OLD '+'.'*20)
            failureTimes=failureTimes+1
            return (1,failureTimes)
    except subprocess.CalledProcessError,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)
    except OSError,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)
    except Exception,msg:
        logCollector(str(msg))
        logCollector('#'*20+'部署任务出现异常'+'#'*20)
        failureTimes=failureTimes+1
        return (1,failureTimes)

def work(cntl_q,data_q):
    session=Session()
    username="root"
    passwd="xiniunet_#*2105"
    host="112.124.121.74"
    item=data_q.get()
    workOrder=item['workOrder']
    family=item['typename']
    projectName=item['modelname']
    version=item['versionnumber']
    remoteTarPath=item['remote_path']
    git_url=item["git_url"]
    localServicePath=item["user_account"]
    deploytype=item["deployType"]
    try:
        info=TaskLogs(id=workOrder,user_id=localServicePath,deploytype=deploytype,family=family,models=projectName,version=version,status="DEPLOYING",failure_time=0,context="NO_LOG")
        session.add(info)
        session.commit()
        if family=='Service':
            (recode,failureTimes)=deployServiceWork(username,passwd,localServicePath,remoteTarPath,version,host,projectName,git_url)
        elif family=='Web':
            (recode,failureTimes)=deployWebWork(username,passwd,localServicePath,remoteTarPath,version,host,projectName,git_url)
        if recode==0:
            status='SUCCESS'
        else:
            status='FAILURE'
        info=TaskLogs(id=workOrder,user_id=localServicePath,deploytype=deploytype,family=family,models=projectName,version=version,status=status,failure_time=failureTimes,context=logText)
        session.merge(info)
        cntl_q.put({'event':'exit','pid':os.getpid()})
    except Exception,msg:
        print msg
        session.rollback()
        cntl_q.put({'event':'exit','pid':os.getpid()})
        raise
    finally:
        session.commit()
        session.close()


def main(cntl_q,data_q):
    proc_pool = {}
    while True:
        if not cntl_q.empty():
            item = cntl_q.get()
            if item['event'] == 'data':
                proc = mp.Process(target=work,args=(cntl_q,data_q))
                proc.start()
                proc_pool[proc.pid] = proc
                print datetime.datetime.now(),"INFO",'###############pack-worker {} started###########'.format(proc.pid)
            elif item['event'] == 'exit':
                proc = proc_pool.pop(item['pid'])
                proc.join()
                print datetime.datetime.now(),"INFO", '###############child {} stopped###############'.format(item['pid'])
            else:
                print 'It\'s impossible !'
        else:
            #print 'cntl_q is empty!!!'
            time.sleep(5)

if __name__ == '__main__':
    pass