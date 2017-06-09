# -*- coding: utf-8 -*-
import ConfigParser
import base64
import json
import os

from flask import request, redirect, url_for, jsonify, session

from spidermanager import app,db
from spidermanager.model.user import User
from spidermanager.setting import managerhosts
from spidermanager.util.action_result import list2json, obj2json

from spidermanager.setting import basedir
from jinja2 import Template

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@app.route("/user/add", methods=['GET','POST'])
def add():

    username = request.form.get('username')
    description = request.form.get('description')
    password = request.form.get('password')
    type = request.form.get('type')
    status = request.form.get('status')
    if(status==None):
        status="stop"
    webuiport = request.form.get('webuiport')
    schedulerport = request.form.get('schedulerport')
    projectdb = request.form.get('projectdb')
    taskdb = request.form.get('taskdb')
    resultdb = request.form.get('resultdb')
    try:
        user = User(username, description, password, type, status, webuiport, schedulerport, projectdb, taskdb, resultdb)
        db.session.add(user)
        db.session.commit()
        resp = {
            "status":"ok",
            "detail":username
        }
    except Exception,e:
        print e
        resp = {
            "status":"error",
            "detail":"无法新增，可能相同ID已存在！"
        }

    return json.dumps(resp)


@app.route("/user/edit", methods=['GET','POST'])
def edit():

    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    user.description = base64.b64encode(request.form.get('description'))
    user.password = request.form.get('password')
    user.type = request.form.get('type')
    user.status = request.form.get('status')
    if(user.status==None):
        user.status="stop"
    user.webuiport = request.form.get('webuiport')
    user.schedulerport = request.form.get('schedulerport')
    user.projectdb = request.form.get('projectdb')
    user.taskdb = request.form.get('taskdb')
    user.resultdb = request.form.get('resultdb')
    try:
        db.session.commit()
        resp = {
            "status":"ok",
            "detail":username
        }
    except Exception,e:
        print e
        resp = {
            "status":"error",
            "detail":"无法修改！"
        }

    return json.dumps(resp)


@app.route("/user/delete", methods=['GET','POST'])
def delete():

    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()

    resp = {
        "status":"ok",
        "detail":username
    }

    return json.dumps(resp)


@app.route("/user/load", methods=['GET','POST'])
def load():
    users = db.session.query(User).all()

    for user in users:
        try:
            user.description = base64.b64decode(user.description)
        except Exception,e:
            print e

    return list2json(users)

@app.route("/user/get", methods=['GET','POST'])
def get():

    username = request.values.get('username')
    user = User.query.filter_by(username=username).first()
    try:
        user.description = base64.b64decode(user.description)
    except Exception,e:
        print e
    return obj2json(user)

@app.route("/user/getlink", methods=['GET','POST'])
def getlink():

    username = request.values.get('username')
    user = User.query.filter_by(username=username).first()
    managerhost = managerhosts[0]
    managerport = user.webuiport
    resp = {
        "link":"http://"+str(managerhost)+":"+str(managerport),
    }
    return json.dumps(resp)

@app.route("/user/start", methods=['GET','POST'])
def start():
    username = request.values.get('username')
    user_type = request.values.get('user_type')
    from spidermanager.service.remote_controller import RemoteController
    rc = RemoteController(username)
    rc.startall(user_type)
    user = User.query.filter_by(username=username).first()
    user.status = "running"
    try:
        db.session.commit()
        resp = {
            "status":"ok",
            "detail":username
        }
    except Exception,e:
        print e
        resp = {
            "status":"error",
            "detail":"无法修改！"
        }
    return json.dumps(resp)

@app.route("/user/loadPhantomjs", methods=['GET','POST'])
def loadPhantomjs():
    try:

        config = ConfigParser.ConfigParser()

        config.readfp(open(basedir+'/setting.ini'))

        ports = config.get("phantomjs","ports")

        list = ports.split(",")

        resp = {
            "startport":list[0],
            "endport":list[len(list)-1]
        }
    except:
        resp = {
            "startport":"startport",
            "endport":"endport"
        }
    return json.dumps(resp)

@app.route("/user/stopPhantomjs", methods=['GET','POST'])
def stopPhantomjs():

    from spidermanager.service.remote_controller import RemoteController
    rc = RemoteController("phantomjs")#Phantomjs日志文件phantomjs.log
    rc.stopPhantomjs()
    return json.dumps({})

@app.route("/user/setPhantomjs", methods=['GET','POST'])
def setPhantomjs():
    startport = request.values.get('startport')
    endport = request.values.get('endport')
    print startport,endport
    f0=open(basedir + "/templates/phantomjs.tpl","r")
    str_f0 = f0.read()
    f0.close()
    tpl = Template(str_f0)
    ports = ""
    serverlist = ""
    base_server_str1="    server 127.0.0.1:"
    base_server_str2=";\n"
    for i in range(int(startport),int(endport)+1):
        if i != int(endport):
            ports = ports+str(i)+","
        else:
            ports = ports+str(i)
        serverlist = base_server_str1 + str(i) + base_server_str2
    content = tpl.render(
        serverlist=serverlist,
    )

    if os.path.exists(basedir + "/tmp/phantomjs.conf"):
        os.remove(basedir + "/tmp/phantomjs.conf")

    f1=open(basedir + "/tmp/phantomjs.conf","wb")
    f1.write(content)
    f1.close()

    config = ConfigParser.ConfigParser()

    config.read(basedir+'/setting.ini')

    config.set("phantomjs", "ports", ports)

    config.write(open(basedir+'/setting.ini', "r+"))

    from spidermanager.service.remote_controller import RemoteController
    rc = RemoteController("phantomjs")#Phantomjs日志文件phantomjs.log
    rc.stopPhantomjs()
    rc.reloadNginxAll()
    rc.startPhantomjs()
    resp = {
        "phantomjsPorts":startport+" to "+endport,
    }
    return json.dumps({})

@app.route("/user/stop", methods=['GET','POST'])
def stop():

    username = request.values.get('username')
    from spidermanager.service.remote_controller import RemoteController
    rc = RemoteController(username)
    rc.killall()
    user = User.query.filter_by(username=username).first()
    user.status = "stop"
    try:
        db.session.commit()
        resp = {
            "status":"ok",
            "detail":username
        }
    except Exception,e:
        print e
        resp = {
            "status":"error",
            "detail":"无法修改！"
        }
    return json.dumps(resp)


@app.route("/user/restart", methods=['GET','POST'])
def restart():

    username = request.values.get('username')
    user_type = request.values.get('user_type')
    from spidermanager.service.remote_controller import RemoteController
    rc = RemoteController(username)
    rc.killall()
    rc.startall(user_type)
    user = User.query.filter_by(username=username).first()
    user.status = "running"
    try:
        db.session.commit()
        resp = {
            "status":"ok",
            "detail":username
        }
    except Exception,e:
        print e
        resp = {
            "status":"error",
            "detail":"无法修改！"
        }
    return json.dumps(resp)
