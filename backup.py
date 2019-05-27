# -*- coding: UTF-8 -*-

import sys
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import DBIO.DBBase as DB
import modules.visitor as visitor
import time,datetime
import threading,traceback
import multiprocessing

reload(sys)
sys.setdefaultencoding('utf-8')

def dateDelta(n_days):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=(-n_days+1))
    n_days = now + delta
    date = n_days.strftime("%Y%m%d")
    return date       

def sourceSync(threadName, delay, station):
    while 1:
        start_time = time.time()
        date = dateDelta(6)
        sql1 = "delete from visitor_source_data where registDate < %s"%date     
        sql2 = "delete from visitor_local_data where registDate < %s"%date
        print "sql1: ",sql1," sql2 : ",sql2
        print "now:",datetime.datetime.now()
        
        DB.DBLocal.query(sql1)
        DB.DBLocal.query(sql2)
        print "TIME COST: %s" % (time.time() - start_time)
        time.sleep(delay)

if __name__ == '__main__':
    args = sys.argv[1:]
    station = map(int, args)
    print station
    print "Source Sync process"
    sourceSync("Sync Process", 50, station=station)
