
# -*- coding: utf-8 -*-

import os
import sys
import logging
import web
import DBIO.DBBase as DB
import common.config as cfg
import json
import copy
import hashlib
from common.func import packOutput
from common.func import checkSession

class WorkerInterface:

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
            resultJson = {"workerNum": num, "workerList": []}
            for item in list:
                worker = item.copy()
                del worker["callerList"]
                resultJson["workerList"].append(worker)
            return packOutput(resultJson)

        elif action == "getInfo":
            worker = self.getInfo(webData)
            return packOutput(worker)

        elif action == "import":
            self.imports(webData)
            return packOutput({})

        elif action == "add":
            id = self.addWorker(webData)
            return packOutput({})

        elif action == "del":
            ret = self.delWorker(webData)
            if ret == -1:
                resultJson = {"result" : "failed"}
            else:
                resultJson = {"result" : "success"}
            return packOutput(resultJson)

        elif action == "edit":
            id = self.editWorker(webData)
            return packOutput({})

        elif action == "testSource":
            ret = self.testImportSource(webData)
            if ret:
                resultJson = {"result" : "success" }
            else:
                resultJson = {"result": "failed"}
            return packOutput(resultJson)

        elif action == "testSourceConfig":
            ret = self.testImportSourceConfig(webData)
            sql = self.getAliasSql(webData)
            if ret:
                resultJson = {"result" : "success" , "sql" : sql}
            else:
                resultJson = {"result": "failed","sql":sql}
            return packOutput(resultJson)

        elif action == "checkID":
            ret = self.checkConflict(webData)
            resultJson = {"conflict": ret}
            return packOutput(resultJson)

        else:
            return packOutput({},"500","unsupport action")


    def getList(self,webData):
        filter = webData["stationID"]
        ret = DB.DBLocal.where('workers',stationID = filter)
        return ret

    def getInfo(self,webData):
        ret = DB.DBLocal.where('workers', stationID = webData["stationID"],id = webData["id"])
        worker = ret[0]
        return worker

    def addWorker(self,inputData):
        # stationID = inputData["stationID"]
        # workerData = copy.deepcopy(inputData)
        # if workerData.has_key("token"):
        #     del workerData["token"]
        # if workerData.has_key("action"):
        #     del workerData["action"]
        # first = 1
        # sql = "insert into workers ( "
        # for key,v in workerData.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += key
        #     first = 0
        # sql += " ) values ( "
        # first = 1
        # for k,value in workerData.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += '\''
        #     sql += str(value)
        #     sql += '\''
        #     first = 0
        # sql += ")"
        # print  "auto sql insert worker : sql " + sql
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(inputData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        print "INSERT INTO workers"
        result = DB.DBLocal.insert("workers", **values)
        return result

    def delWorker(self,webData):
        # id = webData["id"]
        # stationID = webData["stationID"]
        # try:
        #     filter = "id=" + '\''+ str(id) + '\'' +' and stationID = ' + '\'' + str(stationID)  + '\' '
        #     ret = DB.DBLocal.delete('workers',filter)
        #     return ret
        # except Exception, e:
        #     print Exception, ":", e
        #     return -1
        id = webData.get("id")
        stationID = webData.get("stationID")
        try:
            result = DB.DBLocal.delete("workers",
                                       where="id=$id and stationID=$stationID",
                                       vars={"id": id, "stationID": stationID})
            return result
        except Exception, e:
            print Exception, ":", e
            return -1

    def editWorker(self,webData):
        # stationID = webData["stationID"]
        # workerData = copy.deepcopy(webData)
        # if webData.has_key("token"):
        #     del workerData["token"]
        # if webData.has_key("action"):
        #     del workerData["action"]
        #
        # first = 1
        # sql = "update workers set "
        # for key, v in workerData.iteritems():
        #     if first != 1:
        #         sql += ','
        #     sql += key
        #     sql += ' = ' + '\'' + str(v) + '\' '
        #     first = 0
        # sql += " where id = " + '\'' + workerData["id"] + '\' ' +' and stationID = ' + '\'' + str(stationID)  + '\' '
        # print  "auto sql update worker : sql " + sql
        #
        # ret = DB.DBLocal.query(sql)
        # return ret
        data = dict(copy.deepcopy(webData))
        data.pop("token", None)
        data.pop("action", None)
        values = {}
        for key, value in data.iteritems():
            if value is not None:
                values.update({key: value})
        id = values.get("id")
        stationID = values.get("stationID")
        print "UPDATE workers"
        result = DB.DBLocal.update("workers",
                                   where="id=$id and stationID=$stationID",
                                   vars={"id": id, "stationID": stationID}, **values)
        return result

    def imports(self,config):
        self.DBSource = web.database(
            dbn = config["DBType"],
            host = config["host"],
            port = int(config["port"]),
            db = config["DBName"],
            user = config["user"],
            pw = config["passwd"],
            charset = config["charset"]
        )
        tableName = config["table"]
        print "DBSource connect ok " + tableName
        res = self.DBSource.select(tableName)
        view = self.getAliasSql(config)
        print "get view :" + view
        workerList = self.DBSource.select(view)
        for item in workerList:
            item["stationID"] = config["stationID"]
            item["user"] = item["id"]
            item["password"] = "123456"
            self.addWorker(item)
        return

    def getAliasSql(self , config):
        configList = ("aliasID", "aliasName", "aliasTitle", "aliasDepartment", "aliasDescText", "aliasHeadPic")
        paraList = ("id", "name", "title", "department", "descText", "headPic")

        sourceTable = "(SELECT "
        iterPara = iter(paraList)
        dot = 0
        for conf in configList :
            if config[conf] != "":
                if dot == 0:
                    dot = 1
                else:
                    sourceTable += " , "
                sourceTable += config[conf]
                sourceTable += " as " + iterPara.next()
        sourceTable += " from " + config["table"] +") as workerView"

        return sourceTable

    def testImportSource(self, config):
        try:
            self.DBSource = web.database(
                dbn = config["DBType"],
                host = config["host"],
                port = int(config["port"]),
                db = config["DBName"],
                user = config["user"],
                pw = config["passwd"],
                charset = config["charset"]
            )
            tableName = config["table"]
            print "DBSource connect ok " + tableName
            res = self.DBSource.select(tableName)
        except Exception,e:
            print Exception,":",e
            return 0
        return 1

    def testImportSourceConfig(self,config):
        try:
            DBTest = web.database(
                dbn=config["DBType"],
                host=config["host"],
                port=int(config["port"]),
                db=config["DBName"],
                user=config["user"],
                pw=config["passwd"],
                charset=config["charset"]
            )
            viewTest = self.getAliasSql(config)
            res = DBTest.where(viewTest)
        except Exception, e:
            print Exception, ":", e
            return 0
        return 1

    def checkConflict(self,inputData):
        ret = DB.DBLocal.where('workers', stationID = inputData["stationID"],id = inputData["id"])
        if len(ret) > 0:
            return 1
        else:
            return 0


class NginxUploadController:

    def POST(self, *args, **kargs):
        # try:
        print 'args ', args
        print 'kargs ', kargs

        myfile = web.input(myfile={}, uptype="")
        filename = myfile['filename']
        logging.warning('Upload file ' + filename)
        name, ext = os.path.splitext(filename)
        # avoid none ascii issue
        myMd5 = hashlib.md5()

        if isinstance(name, str):
            myMd5.update(name.decode('utf8').encode('utf8'))
        elif isinstance(name, unicode):
            myMd5.update(name.encode('utf8'))

        dirPath = cfg.headPicPath


        name_md5 = myMd5.hexdigest()
        ext = ext.lower()
        newFileName = "%s%s" % (name_md5,ext)
        dest = os.path.join(dirPath, newFileName)


        print myfile['filepath']
        print dest

        os.rename(myfile['filepath'], dest);
        rst = {'result': 0, 'upload_path': cfg.upload_http_base + newFileName, 'size': myfile.size}
        # return '<script>parent.uploadCallback(%s);window.location.href="upload%s.html";</script>'% (json.dumps(rst),myfile.uptype)
        return json.dumps(rst)


    def GET(self, *args, **kargs):
	web.header("Content-Type","text/html; charset=utf-8")
	return """<html><head></head><body>
			  <form method="POST" enctype="multipart/form-data" action="/headpicUpload">
			  <input type="file" name="myfile" />
			  <br/>
			  <input type="submit" />
			  </form>
			  </body></html>"""



class headpicUpload:

    def POST(self):
        myfile = web.input(myfile={}, uptype="")
        filename = myfile['filename']
        logging.warning('Upload file ' + filename)
        name, ext = os.path.splitext(filename)
        # avoid none ascii issue
        myMd5 = hashlib.md5()

        if isinstance(name, str):
            myMd5.update(name.decode('utf8').encode('utf8'))
        elif isinstance(name, unicode):
            myMd5.update(name.encode('utf8'))

        dirPath = cfg.headPicPath

        name_md5 = myMd5.hexdigest()
        ext = ext.lower()
        newFileName = "%s%s" % (name_md5,ext)
        dest = os.path.join(dirPath, newFileName)
        os.rename(myfile['filepath'], dest);
        rst = {'result': "success", 'upload_path': cfg.upload_http_base + newFileName, 'size': myfile.size}
        # return '<script>parent.uploadCallback(%s);window.location.href="upload%s.html";</script>'% (json.dumps(rst),myfile.uptype)
        return packOutput(rst)


class WebUploadController:

    def POST(self,name):
        x = web.input(myfile={})
        filedir = cfg.headPicPath
        if 'myfile' in x:
            filepath = x.myfile.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
            fout = open(filedir + '/' + filename, 'w')  # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read())  # writes the uploaded file to the newly created file.
            fout.close()  # closes the file, upload complete.
            rst = {'result': "success", 'upload_path': cfg.upload_http_base + filename, 'size': x.myfile.size}
            return packOutput(rst)

        raise web.seeother('/upload')
