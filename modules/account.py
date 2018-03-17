
# -*- coding: UTF-8 -*-

import sys
import logging
import web

import common.func
import DBIO.DBBase as DB
import json
import mainWorker
from common.func import packOutput
from caller import CallerInterface


def unicode2str(unicodeStr):
    if type(unicodeStr) == unicode:
        return unicodeStr.encode("utf-8")
    elif type(unicodeStr) == str:
        return unicodeStr
    else:
        return unicodeStr

class LogonInterface:

    def POST(self,name):

        webData = json.loads(web.data())

        user = webData["user"]
        passwd = webData["passwd"]

        if user == "root" and passwd == "clear!@#":
            ret = {"token": common.func.getToken(user,passwd),
                   "userType": "Manager"
                   }
            return packOutput(ret)

        #判断是否为分诊台帐号
        ret = DB.DBLocal.where("account", user=user,password = passwd)
        if len(ret) != 0:
            account = ret[0]
            ret = { "userType": "station","stationID":account["stationID"]}
            ret["token"] = common.func.getToken(user,passwd)
        else:
            #判断是否为医生账号
            ret = DB.DBLocal.where("workers", user=user, password=passwd)

            if len(ret) != 0:
                for account in ret:
                    # 判断是否在允许的叫号器上登录
                    if "localIP" in webData:
                        account["localIP"] = webData["localIP"]
                    caller = mainWorker.WorkerMainController().getCallerInfo(account)
                    if caller != {}:            #不合法的医生账户登录
                        ret = {"userType": "worker","stationID": account["stationID"]}
                        ret["callerID"] = caller["id"]
                        onlineMsg = {"stationID":account["stationID"],"callerID":caller["id"],\
                                     "workerID":account["id"],"status":"online"}
                        CallerInterface().setWorkerStatus(onlineMsg)
                        ret["token"] = common.func.getToken(user,passwd)
                        return packOutput(ret)
                if "localIP" in webData:
                    return packOutput({}, "500", "not allowed caller，ip: " + webData["localIP"])
                else:
                    return packOutput({}, "500", "not allowed caller，ip: " + web.ctx.ip)
            else:
                return packOutput({},"500","uncorrect user and password")

        return packOutput(ret)

    def GET(self,name):
        return 1

class StationAccountInterface:
    def POST(self,name):
        webData = json.loads(web.data())
        action = webData["action"]
        if "token" in webData:
            token = webData["token"]
            if common.func.checkSession(token) == False:
                return packOutput({}, "401", "Tocken authority failed")

        if action == "edit":
            account = {}
            stationID = webData["stationID"]
            account["user"] = webData["user"]
            account["password"] = webData["password"]
            account["descText"] = webData["descText"]
            stationAccount = DB.StationAccount()
            stationAccount.edit(stationID,account)
            return packOutput({})

        elif action == "getList":
            stationAccount = DB.StationAccount()
            resultJson = {"accountList":[]}
            list = stationAccount.getList()
            for item in list:
                resultJson["accountList"].append(item)
            return packOutput(resultJson)

        elif action == "getInfo":
            stationID = webData["stationID"]
            stationAccount = DB.StationAccount()
            info = stationAccount.getInfo(stationID)
            return packOutput(info)