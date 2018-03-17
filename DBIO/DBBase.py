# -*- coding: UTF-8 -*-

import os
from functools import wraps
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import web
import common.config as dbConfig
from common.func import LogOut

configList = ("aliasName", "aliasAge", "aliasQueue", "aliasID", "aliasOrderDate", "aliasOrderTime", "aliasRegistDate",
              "aliasRegistTime", "aliasSnumber" \
                  , "aliasVIP", "aliasOrderType", "aliasWorkerID", "aliasWorkerName", "aliasDepartment",
              "aliasDescText", "aliasStatus","aliasCardID","aliasPersonID","aliasPhone")

paraList = ("name", "age", "queue", "id", "orderDate", "orderTime", "registDate", "registTime", "snumber", \
            "VIP", "orderType", "workerID", "workerName", "department", "descText", "status","cardID","personID","phone")

DBLocal = web.database (
    dbn = 'mysql',
    host = dbConfig.db_host,
    port = int(dbConfig.db_port),
    db = dbConfig.db_name,
    user = dbConfig.db_user,
    pw = dbConfig.db_pass,
    charset = 'utf8'
)

class StationVisitor:
    def __init__(self):
        return

    def newSource(self,config):
        self.config =  config

        id = DBLocal.insert('stationSet', name=config["name"], descText=config["descText"], DBType = config["DBType"], host=config["host"] ,port=config["port"], charset=config["charset"],
            user=config["user"], passwd=config["passwd"], DBName=config["DBName"], tableName=config["tableName"], aliasName=config["aliasName"], aliasAge = config["aliasAge"], aliasQueue = config["aliasQueue"], aliasID = config["aliasID"],
            aliasOrderDate=config["aliasOrderDate"], aliasOrderTime=config["aliasOrderTime"], aliasRegistDate=config["aliasRegistDate"], aliasRegistTime=config["aliasRegistTime"], aliasSnumber=config["aliasSnumber"],
            aliasVIP=config["aliasVIP"], aliasOrderType=config["aliasOrderType"], aliasWorkerID=config["aliasWorkerID"], aliasWorkerName=config["aliasWorkerName"],
            aliasDepartment=config["aliasDepartment"], aliasDescText=config["aliasDescText"], aliasStatus=config["aliasStatus"],aliasCardID = config["aliasCardID"],
            aliasPersonID = config["aliasPersonID"],aliasPhone = config["aliasPhone"],renewPeriod=config["renewPeriod"]
            )
        self.id = id
        LogOut.info("new Station source ok id :" + str(id))
        return id

    def SourceLoad(self,id):
        self.id = id
        LogOut.info("load station id :" + str(self.id))
        ret = DBLocal.where('stationSet',id = self.id)
        LogOut.info( "inquire DB OK")
        #for r in ret:
        config = iter(ret).next()

        if config["DBType"] == "oracle":
            self.DBSource = web.database(
                dbn=config["DBType"] , db=config["host"] , user=config["user"] , pw=config["passwd"]
            )
        elif config["DBType"] == "mssql":
            self.DBSource = MSSQLController(config)
        else:
            self.DBSource = web.database(dbn=config["DBType"],host=config["host"],port=int(config["port"]),db=config["DBName"],user=config["user"],
                pw=config["passwd"],charset=config["charset"]
            )
        self.tableName = self.getTableName(config)
        self.type = config["DBType"]
        LogOut.info("DBSource connect ok " + self.tableName)
        self.view = self.getAliasSql(config)
        LogOut.info( "get view :" + self.view)
        return config

    def testAliasSql(self,config):
        try:
            self.testSource(config)
            viewTest = self.getAliasSql(config)
            res = self.DBTest.where(viewTest)
        except Exception, e:
            print Exception, ":", e
            return 0
        return 1

    def testSource(self,config):
        try:
            if config["DBType"] == "oracle":
                self.DBTest = web.database(
                    dbn = config["DBType"],
                    db = config["host"],
                    user = config["user"],
                    pw = config["passwd"]
                )
                res = self.DBTest.select(self.getTableName(config))
            elif config["DBType"] == "mssql":
                self.DBTest = MSSQLController(config)
                res = self.DBTest.select(self.getTableName(config))

            else:
                self.DBTest = web.database(
                    dbn = config["DBType"],
                    host = config["host"],
                    port = int(config["port"]),
                    db = config["DBName"],
                    user = config["user"],
                    pw = config["passwd"],
                    charset = config["charset"]
                )
                res = self.DBTest.select(config["tableName"])
        except Exception,e:
            print Exception,":",e
            return 0
        return 1

    def getTableName(self, config):
        self.tableName = config["tableName"]
        return self.tableName

    def getColName(self, col):
        if self.type != "oracle":
            return col
        else:
            return col.upper()

    def getAliasSql(self , config):
        self.getTableName(config)
        sourceTable = "(SELECT "
        iterPara = iter(paraList)
        dot = 0
        for conf in configList :
            para = iterPara.next()
            if config[conf] != "":
                if dot == 0:
                    dot = 1
                else:
                    sourceTable += " , "
                sourceTable += config[conf]
                sourceTable += " as " + para
        sourceTable += " from " + self.tableName +") visitorsView"
        return sourceTable

    def getView(self):
        return self.view

    def convertItem(self,item):
        if self.type != "oracle":
            return item
        paraList = ("id","name", "age", "queue",  "orderDate", "orderTime", "registDate", "registTime", "snumber", \
                    "VIP", "orderType", "workerID", "workerName", "department", "descText", "status", "cardID",
                    "personID", "phone")
        ret = {}
        for key in paraList:
            if key.upper() in item:
                ret[key] = item[key.upper()]
        return ret

    def close(self):
        # close cursor
        self.DBSource._db_cursor().close()
        # close connection
        self.DBSource._db_cursor().connection.close()
        del self.DBSource


class MSSQLController(object):
    """对web.py中MSSQLDB的数据库操作方法进行一定的修改"""
    def __init__(self, config):
        self.MSSQLDB = web.database(
            dbn=config["DBType"],
            host=config["host"],
            port=int(config["port"]),
            db=config["DBName"],
            user=config["user"],
            pw=config["passwd"],
            charset=config["charset"]
        )
        self.MSSQLDB.ctx.db.autocommit(True)

    def __getattr__(self, item):
        func = None
        if item in ("query", "select", "where", "insert", "update", "delete"):
            if item == 'query':
                func = self.MSSQLDB.query
            elif item == 'select':
                func = self.MSSQLDB.select
            elif item == 'where':
                func = self.MSSQLDB.where
            elif item == 'insert':
                func = self.MSSQLDB.insert
            elif item == 'update':
                func = self.MSSQLDB.update
            elif item == 'delete':
                func = self.MSSQLDB.delete
            func = mssql_wrapper(func)
        elif item == "_db_cursor":
            func = self.MSSQLDB._db_cursor
        elif item == "dbname":
            func = self.MSSQLDB.dbname
        return func


def mssql_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result = result.list()
        return result
    return wrapper


class StationSet:
    def __init__(self):
        self.vectorSource = StationVisitor()
        self.accout = StationAccount()
        return

    def loadAll(self):
        try:
            ret = DBLocal.select('stationSet')
            return ret
        except Exception, e:
            print Exception, ":", e
            return -1

    def addNew(self,config):
        id = self.vectorSource.newSource(config)
        account ={}
        account["stationID"] = id
        account["user"] = "station" + str(id)
        account["password"] = "123456"
        account["type"] = "station"
        account["descText"] = config["name"]
        self.accout.add(account)
        return id

    def delEntity(self,id):
        try:
            filter = "id=" + str(id)
            ret = DBLocal.delete('stationSet',filter)
            self.accout.delete(id)
            return ret
        except Exception, e:
            print Exception, ":", e
            return -1

    def chgEntity(self,id,config):
        try:
            filter = "id=" + str(id)
            ret = DBLocal.update('stationSet',filter,name=config["name"], descText=config["descText"], DBType = config["DBType"], host=config["host"] ,port=config["port"], charset=config["charset"],
                user=config["user"], passwd=config["passwd"], DBName=config["DBName"], tableName=config["tableName"], aliasName=config["aliasName"], aliasAge = config["aliasAge"], aliasQueue = config["aliasQueue"], aliasID = config["aliasID"],
                aliasOrderDate=config["aliasOrderDate"], aliasOrderTime=config["aliasOrderTime"], aliasRegistDate=config["aliasRegistDate"], aliasRegistTime=config["aliasRegistTime"], aliasSnumber=config["aliasSnumber"],
                aliasVIP=config["aliasVIP"], aliasOrderType=config["aliasOrderType"], aliasWorkerID=config["aliasWorkerID"], aliasWorkerName=config["aliasWorkerName"],
                aliasDepartment=config["aliasDepartment"], aliasDescText=config["aliasDescText"], aliasStatus=config["aliasStatus"], aliasCardID = config["aliasCardID"],
                aliasPersonID = config["aliasPersonID"],aliasPhone = config["aliasPhone"],renewPeriod=config["renewPeriod"]
            )
            return ret
        except Exception, e:
            print Exception, ":", e
            return -1

        return

class StationAccount:
    def add(self,account):
        DBLocal.insert("account", stationID=account["stationID"],user=account["user"],password=account["password"], \
                       type=account["type"],descText=account["descText"])
        return 1

    def getInfo(self,id):
        try:
            ret = DBLocal.where("account", stationID=id)
            return ret[0]
        except Exception, e:
            print Exception, ":", e
            return -1

    def getList(self):
        try:
            ret = DBLocal.select("account")
            return ret
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,stationID,account):
        filter = "stationID = \'" + str(stationID) +"\'"
        try:
            DBLocal.update("account",filter,user=account["user"],password=account["password"],descText=account["descText"])
            return 1
        except Exception, e:
            print Exception, ":", e
            return -1

    def delete(self,stationID):
        filter = "stationID = \'" + str(stationID) + "\'"
        try:
            DBLocal.delete("account", filter)
        except Exception, e:
            print Exception, ":", e
            return -1


