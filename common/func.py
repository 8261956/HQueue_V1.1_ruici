
# -*- coding: UTF-8 -*-

import sys
import json
import logging
import random
import common.config as cfg
from datetime import date
from datetime import datetime
from datetime import timedelta
from web import SQLQuery, SQLParam
from common.memcachewrapper import memcached_wrapper

class JsonExtendEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, timedelta):
            tsec = int(o.seconds)
            hour = tsec/3600
            min = (tsec - hour*3600)/60
            sec = tsec%60
            return str(hour) + ":" + str(min) + ":" + str(sec)
        else:
            return json.JSONEncoder.default(self, o)

def packOutput(detail,code = "200",errorInfo = "none"):
    if code == "200":
        resultJson = {"rescode": "200", "errInfo": "none ", "detail":{}}
        resultJson["detail"]  =detail
    else:
        resultJson = {"rescode": code, "errInfo":errorInfo, "detail": {}}
        resultJson["detail"] = detail
    return json.dumps(resultJson, cls=JsonExtendEncoder)

class LogOut:
    @classmethod
    def warning(cls,arg):
        print arg

    @classmethod
    def debug(cls,arg):
        print arg

    @classmethod
    def error(cls,arg):
        print arg

    @classmethod
    def info(cls, arg):
        pass#print arg

def unicode2str(unicodeStr):
    if type(unicodeStr) == unicode:
        return unicodeStr.encode("utf-8")
    elif type(unicodeStr) == str:
        return unicodeStr
    else:
        return unicodeStr

def list2Str(list):
    strOut = ""
    first = 1
    for id in list:
        if first == 0:
            strOut += ","
        strOut += str(id)
        first = 0
    return strOut

def str2List(str):
    if str == "":
        return []
    else:
        return str.split(',')

def createRandomStr32(length=32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)

def getToken(username, password):
    key = '_'.join(['hqms_adv', 'user', username, createRandomStr32(8)])

    value_json = {}
    value_json['username'] = username
    value = json.dumps(value_json)

    mc = memcached_wrapper.getMemcached()
    mc.set(str(key), value, cfg.memcached_timeout)
    mc.disconnect_all()
    return key

def checkSession( token):
    key = str(token)
    mc = memcached_wrapper.getMemcached()
    value = mc.get(key)
    mc.disconnect_all()
    if value == None:
        return False
    else:
        return True

def multiple_insert_sql(tablename, values):
    """生成批量插入或者更新数据的SQL语句，改编自web.py的multiple_insert方法"""

    if not values:
        return []

    keys = values[0].keys()
    # @@ make sure all keys are valid

    for v in values:
        if v.keys() != keys:
            raise ValueError, 'Not all rows have the same keys'

    sql_query = SQLQuery('INSERT INTO %s (%s) VALUES ' % (tablename, ', '.join(keys)))

    for i, row in enumerate(values):
        if i != 0:
            sql_query.append(", ")
        SQLQuery.join([SQLParam(row[k]) for k in keys], sep=", ", target=sql_query, prefix="(", suffix=")")

    tmp = []
    for key in keys:
        update = "%s=VALUES(%s)" % (key, key)
        tmp.append(update)
    update_sql = ' ON DUPLICATE KEY UPDATE %s' % ', '.join(tmp)

    SQLQuery.join(update_sql, sep="", target=sql_query)

    return sql_query


def CachedGetValue(key):
    try:
        mc = memcached_wrapper.getMemcached()
        value = mc.get(str(key).replace(' ',''))
        mc.disconnect_all()
        if value == None:
            return False
        else:
            return value
    except Exception, e:
        print "Memcached get val error "
        print Exception, ":", e
        print key
        print value

def CahedSetValue(key,value, timeout):
    try:
        mc = memcached_wrapper.getMemcached()
        ret  = mc.set(str(key).replace(' ',''), value, timeout)
        mc.disconnect_all()
        return ret
    except Exception, e:
        print "Memcached set error "
        print Exception, ":", e
        print key
        print value

def CachedClearValue(key):
    try:
        mc = memcached_wrapper.getMemcached()
        mc.delete(str(key).replace(' ',''))
        mc.disconnect_all()
    except Exception, e:
        print "Memcached clear error ,key"
        print Exception, ":", e
        print key

def list2Dict(list):
    d = {}
    for item in list:
        d[str(item["id"])] = item
    return d

