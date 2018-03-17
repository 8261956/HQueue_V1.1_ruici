# -*- coding: utf-8 -*-
import sys
import logging
import os, datetime, math
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import web
import DBIO.DBBase as DB
import json
import copy
import re
import time,datetime
from common.func import packOutput
from common.func import str2List
from common.func import list2Str
from common.func import checkSession
from scene import SceneInterface

class QueueInfoInterface:
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
                queue = item.copy()
                queue["workerLimit"] = str2List(queue["workerLimit"])
                resultJson["list"].append(queue)
            return packOutput(resultJson)

        elif action == "getInfo":
            queueInfo = self.getInfo(webData)
            queueInfo["workerLimit"] = str2List(queueInfo["workerLimit"] )
            return packOutput(queueInfo)

        elif action == "add":
            webData["workerLimit"] = list2Str( webData["workerLimit"])
            ret = self.add(webData)
            return packOutput({})

        elif action == "edit":
            webData["workerLimit"] = list2Str( webData["workerLimit"])
            id = self.edit(webData)
            return packOutput({})

        elif action == "delete":
            ret = self.delete(webData)
            if ret == -1:
                resultJson = {"result": "failed"}
            else:
                resultJson = {"result": "success"}
            return packOutput(resultJson)

        elif action == "getSourceQueueList":
            ret= self.getSourceQueueList(webData)
            jsonData = {"num":len(ret), "list": ret}
            return packOutput(jsonData)

        elif action == "getSceneSupportList":
            ret = self.getSceneSupportList(webData)
            list = []
            for item in ret:
                list.append(item)
            jsonData = {"num":len(ret), "list":list}
            return packOutput(jsonData)

        elif action == "getAvgWaitTime":
            try:
                result = self.getAvgWaitTime(webData)
                return packOutput(result)
            except Exception as errorInfo:
                return packOutput({}, code="400", errorInfo=str(errorInfo))

        else:
            return packOutput({}, "500", "unsupport action")

    def getList(self,inputData):
        # ret = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"])
        stationID = inputData["stationID"]
        sql = "SELECT q.id, q.name, q.stationID, q.descText, q.filter, q.workerOnline, q.workerLimit, " \
              "q.orderAllow, s.id as sceneID, s.name as scene, s.activeLocal FROM queueInfo AS q LEFT JOIN scene " \
              "AS s ON q.sceneID = s.id WHERE q.stationID=%s" % stationID
        ret = DB.DBLocal.query(sql)
        return  ret

    def getInfo(self,inputData):
        # TODO: 如果队列的orderAllow属性以后要放在策略配置中，那此处的查询语句要修改
        # TODO: 如果手动在数据库中删除策略，也应该要能获取到队列信息(sceneID在scene表中不存在如何处理)
        stationID = inputData["stationID"]
        id = inputData["id"]
        sql = "SELECT q.id, q.name, q.stationID, q.descText, q.filter, q.workerOnline, q.workerLimit, " \
              "q.orderAllow, s.id as sceneID, s.name as scene, s.activeLocal FROM queueInfo AS q LEFT JOIN scene " \
              "AS s ON q.sceneID = s.id WHERE q.stationID=%s AND q.id=%s" % (stationID, id)
        # ret = DB.DBLocal.where('queueInfo', stationID=inputData["stationID"],id = inputData["id"])
        ret = DB.DBLocal.query(sql)
        if len(ret) == 0:
            raise Exception("[ERR]: queue not exists.")
        return ret[0]

    def loadScenePara(self,inputData):
        sceneList = DB.DBLocal.where("scene", name = inputData["scene"])
        scene = sceneList[0]
        inputData["activeLocal"] = scene["activeLocal"]
        inputData["orderAllow"] = scene["orderAllow"]
        inputData["rankWay"] = scene["rankWay"]
        #inputData["output"] =

    def getSourceQueueList(self,inputData):
        stationID = inputData["stationID"]
        visitorSource = DB.StationVisitor()
        visitorSource.SourceLoad(stationID)
        sql = "select DISTINCT(queue) from " + visitorSource.getView()
        print sql
        res = visitorSource.DBSource.select(visitorSource.getView(),what="DISTINCT(queue)")
        colName = visitorSource.getColName("queue")
        sourceQueueList = []
        for item in res:
            sourceQueueList.append(item[colName])
        choseQueueList = self.getChoseQueueList(stationID)
        print sourceQueueList
        print choseQueueList
        queueList = list(set(sourceQueueList) - set(choseQueueList))
        return queueList

    def getChoseQueueList(self, stationID):
        queueList = self.getList({"stationID": stationID})
        choseQueueList = []
        for item in queueList:
            filter = item["filter"]
            filter = re.findall(r'queue=\'(.*)\'', filter)
            queue = filter[0]
            choseQueueList.append(queue)
        return choseQueueList

    def getSceneSupportList(self,inputData):
        sceneList = DB.DBLocal.select("scene",what="id,name,descText")
        return sceneList

    def add(self,inputData):
        # TODO: 传入的参数中有scene字段，如果后续将数据库中scene字段删除掉，add方法在插入数据库是也要删除scene字段
        # stationID = inputData["stationID"]
        # data = copy.deepcopy(inputData)
        # # self.loadScenePara(data)
        # if data.has_key("token"):
        #     del data["token"]
        # if data.has_key("action"):
        #     del data["action"]
        # first = 1
        # sql = "insert into queueInfo ( "
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
        #     valueStr = str(value)
        #     us = valueStr.replace("'","\\'")
        #     sql += us
        #     sql += '\''
        #     first = 0
        # sql += ")"
        # print  "auto sql insert queueInfo : sql " + sql
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        data.pop("scene", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO queueInfo"
        result = DB.DBLocal.insert("queueInfo", **values)
        return result

    def delete(self, inputData):
        # id = inputData["id"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\''
        #     ret = DB.DBLocal.delete('queueInfo',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = inputData.get("id")
        try:
            result = DB.DBLocal.delete("queueInfo", where="id=$id", vars={"id": id})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        # stationID = inputData["stationID"]
        # data = copy.deepcopy(inputData)
        # # if data.has_key("scene"):
        # #     self.loadScenePara(data)
        # if inputData.has_key("token"):
        #     del data["token"]
        # if inputData.has_key("action"):
        #     del data["action"]
        #
        # first = 1
        # sql = "update queueInfo set "
        # for key, v in data.iteritems():
        #     if key != "id":
        #         if first != 1:
        #             sql += ','
        #         sql += key
        #         restr = str(v).replace("'", "\\'")
        #         sql += ' = ' + '\'' + restr + '\' '
        #         first = 0
        # sql += " where id = " + '\'' + str(data["id"]) + '\' '
        # print  "auto sql update queueInfo : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        data.pop("scene", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        print "UPDATE queueInfo"
        result = DB.DBLocal.update("queueInfo", where="id=$id", vars={"id": id}, **values)
        return result

    def getAvgWaitTime(self, inputData):
        stationID = inputData.get("stationID", None)
        if stationID is None:
            raise Exception("stationID required.")
        queueID = inputData.get("queueID", None)
        if queueID is None:
            raise Exception("queueID required.")
        queueList = DB.DBLocal.where("queueInfo", stationID=stationID, id=queueID)
        if len(queueList) == 0:
            raise Exception("queue not exists.")

        backupDate = datetime.date.today() - datetime.timedelta(days=60)
        sqlLocalData = "SELECT id, workStartTime, workEndTime FROM visitor_local_data " \
                       "WHERE stationID=%s AND queueID=%s" % (stationID, queueID)
        sqlBackupData = "SELECT id, workStartTime, workEndTime FROM visitor_backup_data " \
                        "WHERE stationID=%s AND queueID=%s AND registDate>='%s'"\
                        % (stationID, queueID, backupDate)
        sql = "(%s) UNION ALL (%s)" % (sqlLocalData, sqlBackupData)
        visitorList = DB.DBLocal.query(sql)

        waitTimeList = []
        count = 0
        for visitor in visitorList:
            try:
                id = visitor["id"]
                workStartTime = visitor["workStartTime"]
                workEndTime = visitor["workEndTime"]
                waitTime = (workEndTime - workStartTime).total_seconds()
                if waitTime <= 0:
                    print "[ignored] visitor %s error: workEndTime should larger than workStartTime" % id
                    count += 1
                    continue
                if waitTime >= 36000:
                    print "[ignored] visitor %s error: workEndTime is much larger" % id
                    count += 1
                    continue
                waitTimeList.append(waitTime)
            except (ValueError, TypeError) as e:
                print "[ignored] visitor %s error: %s" % (id, str(e))
                count += 1
                continue

        print "[station %s, queue %s] total visitors: %d, ignored: %d" % \
              (stationID, queueID, len(visitorList), count)
        if len(waitTimeList) == 0:
            avgWaitTime = 0
        else:
            tmp = (sum(waitTimeList)/len(waitTimeList))/60.0
            avgWaitTime = math.ceil(tmp)
        result = {"stationID": stationID, "queueID": queueID, "avgWaitTime": str(avgWaitTime)}
        return result

    def getWorkDays(self,stationID,queueID):
        queueInfo = self.getInfo({"stationID":stationID ,"id":queueID})
        sceneID = queueInfo["sceneID"]
        sceneInfo = SceneInterface().getSceneInfo({"sceneID":sceneID})
        workDays = sceneInfo["workDays"]
        if not workDays >= 1 :
            workDays = 1
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=(-workDays+1))
        n_days = now + delta
        date = n_days.strftime("%Y%m%d")
        return workDays,date

