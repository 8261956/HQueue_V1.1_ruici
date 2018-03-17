# -*- coding: utf-8 -*-

import sys
import logging
import web
import DBIO.DBBase as DB
import json
import copy
from common.func import packOutput
from common.func import str2List
from common.func import list2Str
from common.func import checkSession


class CallerInterface:

    def POST(self,name):

        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "getList":
            list = self.getList(webData)
            num = len(list)
            resultJson = {"num": num, "list": []}
            for item in list:
                caller = item.copy()
                caller["workerLimit"] = str2List(caller["workerLimit"])
                resultJson["list"].append(caller)
            return packOutput(resultJson)

        elif action == "getInfo":
            caller = self.getInfo(webData)
            caller["workerLimit"] = str2List(caller["workerLimit"])
            return packOutput(caller)

        elif action =="add":
            webData["workerLimit"] = list2Str(webData["workerLimit"])
            ret = self.add(webData)
            return packOutput({})

        elif action == "edit":
            webData["workerLimit"] = list2Str(webData["workerLimit"])
            id = self.edit(webData)
            return packOutput({})

        elif action == "delete":
            ret = self.delete(webData)
            if ret == -1:
                resultJson = {"result" : "failed"}
            else:
                resultJson = {"result" : "success"}
            return packOutput(resultJson)

        elif action == "setWorkerStatus":
            ret = self.setWorkerStatus(webData)
            if ret == -1:
                resultJson = {"result" : "failed"}
            else:
                resultJson = {"result" : "success"}
            return packOutput(resultJson)

        else:
            return packOutput({}, "500", "unsupport action")

    def getList(self,inputData):
        ret = DB.DBLocal.where('caller', stationID=inputData["stationID"])
        return ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('caller', stationID=inputData["stationID"],id = inputData["id"])
        return ret[0]

    def add(self,inputData):
        # stationID = inputData["stationID"]
        # data = copy.deepcopy(inputData)
        # if data.has_key("token"):
        #     del data["token"]
        # if data.has_key("action"):
        #     del data["action"]
        # first = 1
        # sql = "insert into caller ( "
        # for key, v in data.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += key
        #     first = 0
        # sql += " ) values ( "
        # first = 1
        # for k, value in data.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += '\''
        #     restr = str(value).replace("'", "\\'")
        #     sql += restr
        #     sql += '\''
        #     first = 0
        # sql += ")"
        # print  "auto sql insert caller : sql " + sql
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO caller"
        result = DB.DBLocal.insert("caller", **values)
        return result

    def delete(self, inputData):
        # id = inputData["id"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\''
        #     ret = DB.DBLocal.delete('caller',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("caller", where="id=$id", vars={"id": id})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        # stationID = inputData["stationID"]
        # data = copy.deepcopy(inputData)
        # if inputData.has_key("token"):
        #     del data["token"]
        # if inputData.has_key("action"):
        #     del data["action"]
        #
        # first = 1
        # sql = "update caller set "
        # for key, v in data.iteritems():
        #     if key != "id":
        #         if first != 1:
        #             sql += ','
        #         sql += key
        #         restr = str(v).replace("'", "\\'")
        #         sql += ' = ' + '\'' + restr + '\' '
        #         first = 0
        # sql += " where id = " + '\'' + str(data["id"]) + '\' '
        # print  "auto sql update caller : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        print "UPDATE caller: %s" % id
        result = DB.DBLocal.update("caller", where="id=$id", vars={"id": id}, **values)
        return result

    #设置登录的在线工作人员
    def setWorkerStatus(self,inputData):
        if inputData["status"] == "online":
            self.edit({"id": inputData["callerID"], "workerOnline": inputData["workerID"], "stationID":inputData["stationID"]})
        else:
            self.edit({"id": inputData["callerID"], "workerOnline": " ", "stationID":inputData["stationID"]})