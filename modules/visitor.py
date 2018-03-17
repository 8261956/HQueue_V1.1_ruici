
# -*- coding: utf-8 -*-

import sys
import logging
import web
import DBIO.DBBase as DB
import json
import copy
import queueInfo
import common.config as cfg
from common.func import packOutput
from common.func import LogOut
from queueData import VisitorLocalInterface
from queueData import QueueDataController
from mainStation import StationMainController
from queueInfo import QueueInfoInterface
import time
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

class VisitorManager:
    def __init__(self):
        self.stationID = 0
        self.queueList = []
        self.VistorSource = DB.StationVisitor()
        self.DBLocal = DB.DBLocal
        self.queueInfo = queueInfo.QueueInfoInterface()
        self.visitorList = []
        pass

    def syncSource(self):
        self.queueList = self.queueInfo.getList({"stationID" : self.stationID})
        LogOut.info("station " + str(self.stationID) + "syncSource" )
        self.getOldTime()
        #scan all queue in a station
        self.VistorSource.SourceLoad(self.stationID)
        dbname = self.VistorSource.DBSource.dbname
        for queue in self.queueList:
            # find the visitors match  queue filtery
            filter =queue["filter"]
            # 日期时间拼接判断
            #     # TODO: 最好registeDate是日期类型， registTime是时间类型;
            #     # TODO: 否则Oracle数据库提供这两个字段的字符串类型
            # 直接按照日期进行判断
            if dbname == 'oracle':
                # TODO: 以下语句针对于registDate是日期或者日期时间的类型，但是插入数据库时因为类型问题会出现warning
                #dataFilter = "and registDate > timestamp\'" + self.oldDataTime + "\'"
                registDateTime = "to_date(to_char(registDate, 'yyyy-mm-dd'), 'yyyy-mm-dd')"
                dataFilter = "%s AND %s = to_date('%s', 'yyyy-mm-dd')" % (filter, registDateTime, self.currentDate)
            elif dbname == 'mssql' or dbname == 'mysql':
                dataFilter = "%s AND registDate = '%s'" % (filter, self.currentDate)

            LogOut.info("queue id " + str(queue["id"]) + " filter " + str(queue["filter"]) + dataFilter)
            start_time = time.time()
            sourcelist = self.VistorSource.DBSource.select(self.VistorSource.getView(),where=dataFilter)
            print "TIME COST: %s" % (time.time() - start_time)

            sourceMap = {}
            for sourceItem in sourcelist:
                sourceItem = self.VistorSource.convertItem(sourceItem)
                #患者ID统一为字符串类型来处理同步
                sourceMap[str(sourceItem["id"])] = str(sourceItem["id"])
                LogOut.info("visitor " + str(sourceItem["id"]) + " finding ")
                localData = self.DBLocal.where("visitor_source_data", id = sourceItem["id"],stationID = self.stationID)
                if len(localData) == 0:
                    #new visitor
                    sourceItem["stationID"] = self.stationID
                    sourceItem["queueID"] = queue["id"]
                    LogOut.info("find visitor " + str(sourceItem["id"]) + " not exist add")
                    interface = VisitorSourceInterface(self.stationID)
                    interface.add(sourceItem)
                else:
                    #old visitor
                    visitor = iter(localData).next()
                    # compare if need update
                    if self.compSource(sourceItem, visitor) != 0:
                        LogOut.info("not same item")
                        LogOut.info("find visitor " + str(sourceItem["id"]) + " exist update")
                        sourceItem["stationID"] = self.stationID
                        interface = VisitorSourceInterface(self.stationID)
                        interface.edit(sourceItem)
                    else:
                        LogOut.info("same item")
                    pass

            #数据源删除数据的检测 删除的患者状态设置为已移除
            if cfg.AutoSyncFinish == '1':
                print "AutoSyncFinish Start:"
                dataFilter = "stationID = %d AND %s AND registDate = '%s'" % (self.stationID, filter, self.currentDate)
                vlist = self.DBLocal.select("visitor_source_data", where=dataFilter)
                for item in vlist:
                    id = item["id"]
                    if item["status"] != "护士新增":
                        #患者已经不在数据源视图中
                        if id not in sourceMap:
                            print "检测到患者从视图中删除将同步到完成态"
                            print id
                            print sourceMap
                            #过滤掉复诊的完成的患者
                            try:
                                visitorList = DB.DBLocal.select("visitor_local_data",
                                                                where="stationID=$stationID and id=$id",
                                                                vars={"stationID": self.stationID, "id": id})
                                vLocalData = visitorList[0]
                                if vLocalData["prior"] != 1 and vLocalData["prior"] != 2 and vLocalData["status"] != "finish":
                                    vStatus = {"id":id, "stationID":self.stationID, "finish":1 }
                                    StationMainController().visitorFinishSet(vStatus)
                            except Exception, e:
                                    print Exception, ":", e


        self.VistorSource.close()

    def syncLocal(self):
        self.queueList = self.queueInfo.getList({"stationID" : self.stationID})
        print("station " + str(self.stationID) + "syncLocal" )
        #scan all queue in a station
        for queue in self.queueList:
            para = {"stationID":self.stationID , "queueID":queue["id"]}
            QueueDataController().updateVisitor(para)
        print "stationID %d  local sync ok" % self.stationID

    def getOldTime(self):
        now = int(time.time())
        buckupTime = now - int(cfg.backupTime)
        deadTime = now - int(cfg.deadTime)

        self.currentDate = time.strftime("%Y-%m-%d", time.localtime(now))
        self.oldData = time.strftime("%Y-%m-%d", time.localtime(buckupTime))
        self.oldTime = time.strftime("%H:%M:%S", time.localtime(buckupTime))
        self.oldDataTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(buckupTime))

        self.invalidData = time.strftime("%Y-%m-%d", time.localtime(deadTime))
        self.invalidTime = time.strftime("%H:%M:%S", time.localtime(deadTime))
        print "get Old Date :" + self.oldData
        print "get Old Time :" + self.oldTime
        print "get Old DateTime :" + self.oldDataTime
        print "get invalid Date :" + self.invalidData
        print "get invalid Time :" + self.invalidTime

    #已完成叫号过时间的视图
    def backupView(self,stationID):
        self.getOldTime()
        joinView = "(select id,status as localStatus,workStartTime,workEndTime from visitor_local_data where stationID =" + str(stationID) +") as joinView"
        joinSql = "select * from visitor_source_data  a inner join " + joinView + " on a.id=joinView.id and a.stationID=" + str(stationID) \
                    + " where (localStatus = 'finish' or localStatus = 'pass') and (workEndTime < \'"+ self.oldDataTime + "\')"
        print ("join sql: " + joinSql)
        return joinSql

    #未叫号的过时间的视图 失效时间判断
    def uncallView(self,stationID):
        self.getOldTime()
        joinView = "(select id,status as localStatus,workStartTime,workEndTime from visitor_local_data where stationID =" + str(stationID) +") as joinView"
        joinSql = "select * from visitor_source_data  a inner join "+ joinView + " on a.id=joinView.id and a.stationID = " +str(stationID) \
                + " where registDate < \'" + self.invalidData + "\' or (registDate = \'" + self.invalidData + "\' and registTime < \'" + self.invalidTime + "\')"
        print ("join sql: " + joinSql)
        return joinSql

    def backupOld(self):
        queueList = self.queueInfo.getList({"stationID": self.stationID})
        LogOut.info("station %d backupOld" % self.stationID)

        #遍历分诊台的队列
        for queue in queueList:
            #得到策略的工作时间
            workDays, dateStr = QueueInfoInterface().getWorkDays(self.stationID, queue["id"])
            joinView = "(select id, queueID, status as localStatus,workStartTime,workEndTime from visitor_local_data where stationID = %d and queueID = %d) as joinView" \
                        %(self.stationID , queue["id"])
            joinSql = "select * from visitor_source_data  a inner join %s on a.id=joinView.id where registDate < %s" % (joinView , dateStr)
            print ("backupView sql: " + joinSql)

            # find the visitors outof date
            backupList = self.DBLocal.query(joinSql)
            for item in backupList:
                print "find backup item name: " + item["name"] + " registDate: " + str(item["registDate"]) + " workEndTime: " + str(item["workEndTime"])
                BackupTableInterface(self.stationID).add(item)
                VisitorSourceInterface(self.stationID).delete(item)
                VisitorLocalInterface(self.stationID).delete(item)

        """
        # find the visitors outof date
        backupList = self.DBLocal.query(self.backupView(self.stationID))
        for item in backupList:
            print "find backup item name: " + item["name"] + " registDate: " + str(item["registDate"]) + " workEndTime: " + str(item["workEndTime"])
            BackupTableInterface(self.stationID).add(item)
            VisitorSourceInterface(self.stationID).delete(item)
            VisitorLocalInterface(self.stationID).delete(item)

        #find the visitors uncall and move to backup
        backupList = self.DBLocal.query(self.uncallView(self.stationID))
        for item in backupList:
            print "find backup item name: " + item["name"] + " registDate: " + str(item["registDate"])
            BackupTableInterface(self.stationID).add(item)
            VisitorSourceInterface(self.stationID).delete(item)
            VisitorLocalInterface(self.stationID).delete(item)
        """

    def compSource(self,source,local):
        for k,v in source.iteritems():
            if k == 'registTime':
                continue
            if k == 'registDate':
                continue
            if str(local[k]) != str(v):
                print "unmatch source "+ str(v)+ " local " + str(local[k])
                return -1
        return 0

class VisitorSourceInterface:
    def __init__(self,stationID):
        self.stationID = stationID

    def getList(self,inputData):
        ret = DB.DBLocal.where('visitor_source_data', queue=inputData["queue"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('visitor_source_data', id = inputData["id"],stationID = self.stationID)
        return ret[0]

    def add(self,inputData):
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO visitor_source_data"
        result = DB.DBLocal.insert("visitor_source_data", **values)
        return result

    def delete(self, inputData):
        id = inputData.get("id")
        stationID = self.stationID
        try:
            result = DB.DBLocal.delete("visitor_source_data",
                                       where="id=$id and stationID=$stationID",
                                       vars={"id": id, "stationID": stationID})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        stationID = self.stationID
        print "UPDATE visitor_source_data"
        result = DB.DBLocal.update("visitor_source_data",
                                   where="id=$id and stationID=$stationID",
                                   vars={"id": id, "stationID": stationID}, **values)
        return result


class BackupTableInterface:
    def __init__(self,stationID):
        self.stationID = stationID

    def getList(self,inputData):
        ret = DB.DBLocal.where('visitor_backup_data', queue=inputData["queue"])
        return  ret

    def getInfo(self,inputData):
        ret = DB.DBLocal.where('visitor_backup_data', id = inputData["id"],stationID = self.stationID)
        return ret[0]

    def add(self,inputData):
        # data = copy.deepcopy(inputData)
        # first = 1
        # sql = "insert into visitor_backup_data ( "
        # for key, v in data.iteritems():
        #     if v == "None":
        #         continue
        #     if first != 1:
        #         sql += ','
        #     sql += key
        #     first = 0
        # sql += " ) values ( "
        # first = 1
        # for k, value in data.iteritems():
        #     if v == "None":
        #         continue
        #     if first != 1:
        #         sql += ','
        #     sql += '\''
        #     restr = str(value).replace("'", "\\'")
        #     sql += restr
        #     sql += '\''
        #     first = 0
        # sql += ")"
        # print  "auto sql insert visitor_backup_data : sql " + sql
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO visitor_backup_data"
        result = DB.DBLocal.insert("visitor_backup_data", **values)
        return result

    def delete(self, inputData):
        # id = inputData["id"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\' and stationID = ' + str(self.stationID)
        #     ret = DB.DBLocal.delete('visitor_backup_data',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = inputData.get("id")
        stationID = self.stationID
        try:
            result = DB.DBLocal.delete("visitor_backup_data",
                                       where="id=$id and stationID=$stationID",
                                       vars={"id": id, "stationID": stationID})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def edit(self,inputData):
        # data = copy.deepcopy(inputData)
        # first = 1
        # sql = "update visitor_backup_data set "
        # for key, v in data.iteritems():
        #     if key != "id":
        #         if first != 1:
        #             sql += ','
        #         sql += key
        #         restr = str(v).replace("'", "\\'")
        #         sql += ' = ' + '\'' + restr + '\' '
        #         first = 0
        # sql += " where id = " + '\'' + str(data["id"]) + '\' and stationID = ' + str(self.stationID)
        # print  "auto sql update visitor_backup_data : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        stationID = self.stationID
        print "UPDATE visitor_backup_data"
        result = DB.DBLocal.update("visitor_backup_data",
                                   where="id=$id and stationID=$stationID",
                                   vars={"id": id, "stationID": stationID}, **values)
        return result


"""
visitor_id = item["id"]
visitor_active_local = 0
visitor_locked = 0
# todo if item haskey "VIP"  and check vip value
visitor_prior = 0
visitor_vip = item["VIP"]
visitor_queue = queue["id"]
visitor_origin_score = item["VIP"]
"""
