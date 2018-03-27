# -*- coding: UTF-8 -*-

import sys
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import DBIO.DBBase as DB
import modules.visitor as visitor
import time
import threading
import multiprocessing

reload(sys)
sys.setdefaultencoding('utf-8')

# 每个线程的工作任务
# def thread(delay, stationID):
#     time.sleep(delay)
#     visitorManager = visitor.VisitorManager()
#     visitorManager.stationID = stationID
#     visitorManager.backupOld()
#     try:
#         visitorManager.syncSource()
#     except Exception as e:
#         print str(e)

def sourceSync(threadName, delay, station):
    print "Source Sync process"
    # 获得分诊台的列表
    stationList = []
    if not station:
        ret = DB.DBLocal.select('stationSet')
        for item in ret:
            stationList.append(item["id"])
    elif all([x < 0 for x in station]):
        ret = DB.DBLocal.select('stationSet')
        for item in ret:
            id = item["id"]
            if id in map(abs, station):
                continue
            else:
                stationList.append(id)
    else:
        stationList = station
    print stationList

    # TODO: 多线程同步数据还需要考虑运行的稳定性
    # threadList = []
    # while 1:
    #     start_time = time.time()
    #     for station in stationList:
    #         t = threading.Thread(target=thread, args=(delay, station))
    #         t.start()
    #         threadList.append(t)
    #
    #     for t in threadList:
    #         t.join()
    #
    #     print "TIME COST: %s" % (time.time() - start_time)
    num = len(stationList)

    counter = 0
    while 1:
        start_time = time.time()
        time.sleep(delay)
        # try:
        # 同步每个分诊台数据
        stationID = stationList[counter % num]
        visitorManager = visitor.VisitorManager()
        visitorManager.stationID = stationID
        if (counter/num) == 0:
            visitorManager.backupOld()
        try:
            #visitorManager.syncSource()
            pass
        except Exception as e:
            print str(e)
        try:            
            pass
            #visitorManager.syncLocal()
        except Exception as e:
            print str(e)
        # wavPreload(station["id"]).load()
        # 计数
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter += 1
        # if (counter % num) == 0:
        #     # 更新分诊台的列表
        #     ret = DB.DBLocal.select('stationSet')
        #     stationList = []
        #     for item in ret:
        #         stationList.append(item['id'])
        #     num = len(stationList)

        if (counter / num) >= 10:
            counter = 0
            print "auto exit to clean up."
            #break

        print "TIME COST: %s" % (time.time() - start_time)


if __name__ == '__main__':
    args = sys.argv[1:]
    station = map(int, args)
    print station
    print "Source Sync process"
    sourceSync("Sync Process", 3000, station=station)
