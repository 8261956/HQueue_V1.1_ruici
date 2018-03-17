# -*- coding:utf-8 -*-

import ConfigParser
import os,sys
import json
import time
import codecs
import requests
import datetime

from common.func import CachedGetValue, CahedSetValue

_config = ConfigParser.ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
stationID = int(_config.get("station", "stationID"))
server = _config.get("station", "server")
htmlPath = _config.get("station", "htmlPath")


headers = {
    'content-type': 'application/json',
}

class StationPrinter(object):

    def __init__(self):
        self.stationID = stationID

    def run(self):
        key = "print_stationID_{0}".format(self.stationID)

        while True:
            queue = CachedGetValue(json.dumps(key))
            while len(queue):
                result = queue.popleft()
                CahedSetValue(json.dumps(key), queue, timeout=0)
                current_time = datetime.datetime.now()
                print "[{0}] new visitor: {1}".format(current_time, result)
            time.sleep(2)

    def reqNewVisitor():
        data = {
            'action':"getNextVisitor",
            'stationID':self.stationID,
        }
        html = requests.post(urlBase + 'aqms/main/printer',data = json.dumps(data),headers = headers)
        result = html.json()
        

    def test(self):
        visitorInfo = {
            "department" : "儿科",
            "snumber" : "12",
            "queue" : "采血1"
        }
        Printer().print2File(visitorInfo,htmlPath)


class Printer():
    def __init__(self):
        self.floderbase = self.cur_file_dir_win()

    # 获取脚本文件的当前路径
    def cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def cur_file_dir_win(self):
        dir = self.cur_file_dir()
        win_dir = dir.replace("/", "\\") + "\\"
        print ("runing dir_win " + win_dir)
        return win_dir

    def print2File(self,visitorInfo, htmlPath):
        with open(htmlPath, 'r') as f:
            fileContent =  f.read()
            fileContent.replace("STRING_PARTMENT",visitorInfo.get("department"))
            fileContent.replace("STRING_SNUMBER", str(visitorInfo.get("snumber")))
            fileContent.replace("STRING_QUEUE", visitorInfo.get("queue"))
            fileContent.replace("STRING_TIME", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            with open("temp.html",'w+') as tf:
                tf.write(fileContent)
                self.runPrinter()

    def runPrinter(self):
        path = self.floderbase + "style4.html"
        cmd = self.floderbase + "printhtml.exe " + " " + "file=" + path
        print cmd
        os.chdir(self.floderbase)
        output = os.popen(cmd)
        print output
        return




if __name__ == '__main__':
    station_printer = StationPrinter()
    station_printer.run()
    #station_printer.test()
