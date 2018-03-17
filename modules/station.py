# -*- coding: UTF-8 -*-

import sys
import logging
import web
import common.func
import DBIO.DBBase as DB
import json
import copy
import visitor
from common.func import packOutput
from common.func import checkSession


class StationManager:
    def __init__(self):
        self.stationList = []
        self.DBIO = DB.StationSet()
        self.LoadStation()

    def LoadStation(self):
        self.stationList = []
        # Read all station list from DB
        list = self.DBIO.loadAll()
        if  list == -1:
            return -1
        else:
            size = 0
            for item in list:
                oneStation = Station()
                oneStation.load(item)
                self.stationList.append(oneStation)
                size += 1
            print(" load stationList func ok ,station num " + str(size))
            return size

    def addStation(self,config):
        print "Add new station to DB"
        id = self.DBIO.addNew(config)
        oneStation = Station()
        oneStation.config(id,config)
        self.stationList.append(oneStation)
        print "Add new station to DB OK , new id " + str(id)
        return id
        # Add new commit Station to DB

    def delStation(self,id):
        print "del station to DB id : " + str(id)
        ret =  self.DBIO.delEntity(id)
        for item in self.stationList:
            if item .getData()["id"] == id:
                self.stationList.remove(item)
        print "del station to DB OK  num : " + str(ret)
        return ret

    def chgStation(self,id,config):
        ret = self.DBIO.chgEntity(id,config)
        for item in self.stationList:
            if item .getData()["id"] == id:
                item.config(id,config)
        print "config station to DB OK id : " + str(id)
        return 1

    def getStation(self,id):
        for item in self.stationList:
            data = item.getData()
            if data["id"] == id:
                print "getStation ok id " + str(id)
                return data
        return {}

class Station:
    def __init__(self):
        self.data = {"queueList":[], "workerList":[], "callerList":[]}
        return

    def load(self,data):
        self.data = data
        self.visitorManager = visitor.VisitorManager()
        self.visitorManager.stationID = self.data["id"]
        #self.visitorManager.syncSource()
        return 1

    def config(self,id,config):
        self.data["id"] = id
        for para in DB.configList :
            self.data[para] = config[para]
        return 1

    def getData(self):
        return self.data

stationMagager = StationManager()

class StationInterface:
    def __init__(self):
        pass

    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "getList":
            print(" Controller  get stationList func in")
            num = stationMagager.LoadStation()
            if num == -1:
                return packOutput({},"500", "getStationList Error")
            else:
                resultJson = {"stationNum": num, "stationList": []}
                for item in stationMagager.stationList:
                    station = {}
                    station['id'] = item.getData()["id"]
                    station['name'] = item.getData()["name"]
                    resultJson['stationList'].append(station)
                print " get stationList func ok ,station num " + str(num)
                return packOutput(resultJson)

        elif action == "getInfo":
            print (" Controller get stationInfo ")
            req = json.loads(web.data())
            stationID = req["stationID"]

            ret = stationMagager.getStation(stationID)
            if ret == {}:
                return packOutput({},"500", "getStationInfo Error")
            else:
                return packOutput(ret)

        elif action == "add":
            print(" Controller  Add station ")
            addObj = json.loads(web.data())
            try:
                id = stationMagager.addStation(addObj)
                resultJson = {"stationID": id}
                return packOutput(resultJson)
            except Exception, e:
                print Exception, ":", e
                return packOutput({},"500","Add station error : " + str(e))

        elif action == "delete":
            print(" Controller  del station ")
            req = json.loads(web.data())
            id = req["stationID"]
            ret = stationMagager.delStation(id)
            if ret == -1:
                return packOutput({}, "500", "del station error" )
            else:
                return packOutput({})

        elif action == "edit":
            print(" Controller  change station ")
            req = json.loads(web.data())
            id = req["stationID"]
            config = req
            ret = stationMagager.chgStation(id, config)
            if ret == -1:
                return packOutput({}, "500", "change station error")
            else:
                return packOutput({})

        elif action == "sourceTest":
            print(" Controller  source Test  ")
            req = json.loads(web.data())
            source = DB.StationVisitor()
            ret = source.testSource(req)
            if ret == 1:
                resultJson = {"testResult": "success"}
            else:
                resultJson = {"testResult": "failed"}
            return packOutput(resultJson)

        elif action == "sourceConfigTest":
            print(" Controller  source config test ")
            req = json.loads(web.data())
            source = DB.StationVisitor()
            ret = source.testAliasSql(req)
            sql = source.getAliasSql(req)
            if ret == 1:
                resultJson = {"testResult": "success", "testSql": sql}
            else:
                resultJson = {"testResult": "failed", "testSql": sql}
            return packOutput(resultJson)

        else:
            return packOutput({},"500","unsupport action")


