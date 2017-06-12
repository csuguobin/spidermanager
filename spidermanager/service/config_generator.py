# -*- coding: utf-8 -*-
import ConfigParser
import os

from jinja2 import Template

from spidermanager.model.user import User
from spidermanager.setting import basedir

def generate_config(username):

    config = ConfigParser.ConfigParser()

    config.readfp(open(basedir+'/setting.ini'))

    ports = config.get("phantomjs","ports")

    filename = basedir + "/tmp/"+ username +".json"

    f0=open(basedir + "/templates/config.tpl","r")

    str_f0 = f0.read()

    f0.close()

    tpl = Template(str_f0)
    if username=="phantomjs":#只用来过滤启动phantomjs组件,其余组件不用考虑
        config =  tpl.render(
            taskdb="",
            projectdb="",
            resultdb="",
            schedulerhost="",
            schedulerport="",
            username="",
            webuiport="",
            password="",
            ports=ports
        )
    else:
        user = User.query.filter_by(username=username).first()
        config =  tpl.render(
            taskdb=user.taskdb,
            projectdb=user.projectdb,
            resultdb=user.resultdb,
            schedulerhost="127.0.0.1",
            schedulerport=user.schedulerport,
            username=user.username,
            webuiport=user.webuiport,
            password=user.password,
            ports=ports
        )


    if os.path.exists(filename):
      os.remove(filename)

    f1=open(filename,"wb")

    f1.write(config)

    f1.close()

    return filename

# generate_config("aaaaaaaa")






