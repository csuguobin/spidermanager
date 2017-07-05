# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, session

from spidermanager import app
from spidermanager.model.admin import Admin
from spidermanager.model.user import User
from spidermanager.setting import managerhosts,SQLALCHEMY_DATABASE_URI
import sqlalchemy.exc
from sqlalchemy import (create_engine, MetaData, Table, Column,
                        String, Float, LargeBinary)


@app.route("/show/load_dict", methods=['GET','POST'])
def load_dict():
    dicts = []
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True,
                               pool_recycle=3600)
        for res in engine.execute("select * from dict_spd_data"):
            dicts.append(res)
    except sqlalchemy.exc.SQLAlchemyError:
        pass
    print dicts
    return list2json(dicts)

@app.route("/show/table_detail", methods=['GET','POST'])
def table_detail(table_name):
    table_detail=[]
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True,
                               pool_recycle=3600)
        for res in engine.execute("select * from %s limit 3"%table_name):
            dicts.append(res)
    except sqlalchemy.exc.SQLAlchemyError:
        pass 
    print table_detail   
    return list2json(table_detail)
