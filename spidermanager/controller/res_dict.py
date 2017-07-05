# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, session

from spidermanager import app
from spidermanager.setting import SHOW_DATABASE_URI
import sqlalchemy.exc
from spidermanager.util.action_result import list2json, obj2json
from sqlalchemy import (create_engine, MetaData, Table, Column,
                        String, Float, LargeBinary)
import json

engine = create_engine(SHOW_DATABASE_URI, convert_unicode=True,pool_recycle=3600)
@app.route("/show/load_dict", methods=['GET','POST'])
def load_dict():
    dicts = []
    try:
        for res in engine.execute("select TBL_ID,MODEL_TBL_DESC,MODEL_TBL_SPD,MODEL_TBL_TYPE,DATA_SOURCE,TOTAL_RECORDS,LAST_UPDATE from dict_spd_data where STATUS in ('A','P')"):
            tmp_dict = {}
            tmp_dict['tableId'] = res[0]
            tmp_dict['tableName'] = res[1]
            tmp_dict['spdTableName'] = res[2]
            tmp_dict['tableType'] = res[3]
            tmp_dict['dataSource'] = res[4]
            tmp_dict['totalRecords'] = res[5]
            tmp_dict['lastUpdate'] = res[6]
            dicts.append(tmp_dict)
    except sqlalchemy.exc.SQLAlchemyError,e:
        print e
    return json.dumps(dicts,ensure_ascii=False)

@app.route("/show/table_detail", methods=['GET','POST'])
def table_detail():
    table_name = request.values.get('table_name')
    table_detail = {}
    tableDesc = []
    sampleData = {}
    col_name = []
    try:
        for res in engine.execute("SELECT column_name, comments FROM user_col_comments where table_name = '%s'"%table_name):
            tmp = {}
            tmp['columnName']=res[0]
            tmp['columnDesc']=res[1].decode('gbk').encode('utf8')
            col_name.append(res[0])
            tableDesc.append(tmp)
        sql = "select %s from %s where rownum=1"%(",".join(col_name),table_name)
        for res in engine.execute(sql):
            for i in range(len(res)):
                sampleData[col_name[i]] = res[i]
        table_detail['tableDesc'] = tableDesc 
        table_detail['sampleData'] = sampleData 
    except sqlalchemy.exc.SQLAlchemyError,e:
        print e 
    return json.dumps(table_detail,ensure_ascii=False)
