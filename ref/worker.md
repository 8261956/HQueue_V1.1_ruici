#工作站管理工作人员信息的接口

## 获取工作人员列表
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "getList",
  "stationID" : 6
}
```
返回内容:

```
{ 
  "errInfo": "none",
  "rescode": "200"
  "detail":{
      "workerNum": 2,
      "workerList": [
        {
          "name": "王医生",
          "title": "主任",
          "headPic": "/headPic/wang",
          "descText": "擅长各种疑难杂症",
          "stationID": 6,
          "user": "wang",
          "department": "超声科",
          "password": "123456",
          "id": ""
        },
        {
          "name": "王医生2",
          "title": "主任",
          "headPic": "/headPic/wang",
          "descText": "擅长各种疑难杂症",
          "stationID": 6,
          "user": "wang2",
          "department": "超声科",
          "password": "123456",
          "id": "D001"
        }
      ],
  }
}
```

##获取工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "getInfo",
  "stationID" : 6,
  "id" : "D001"
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
      "name": "王医生2",
      "title": "主任",
      "headPic": "/headPic/wang",
      "descText": "擅长各种疑难杂症",
      "stationID": 6,
      "user": "wang2",
      "department": "超声科",
      "password": "123456",
      "id": "D001",
      "callerList": "[{},{}]"
  }
}
```

##从数据源导入工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:
```
{
  "token": " safe action",
  "action" : "import",
  "stationID": 2,
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "table" : "workers_import",
  
  "aliasID" : "id",
  "aliasName":"name",
  "aliasTitle":"title",
  "aliasDepartment":"department",
  "aliasDescText":"descText",
  "aliasHeadPic" : ""
}
```
必填项目： aliasID,aliasName 用户不填的传递""
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
   }
}
```

##手动添加工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
{
  "token": " safe action",
  "action": "add",
  "id" : "D001",
  "stationID" :  6,
  "name" : "王医生2",
  "user" : "wang2",
  "password" : "123456",
  "title" : "主任",
  "department" : "超声科",
  "descText" : "擅长各种疑难杂症",
  "headPic" : "/headPic/wang",
  "callerList" : "[{},{}]"
}
```

默认的用户名为工作者ID_工作站ID，默认密码123456  
例如 工作站4的工作者ID D003  用户名默认为D003_4


返回内容:
```
{
   "errInfo": "none",
   "rescode": "200",
   "detail":{
   }
}
```

## 删除一个工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "del",
  "stationID": 2,
  "id" : "D003"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
        "result": "success"
   }
}
```
##修改一个工作者信息
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "edit",
  "stationID" : 6,
  "id" : "D001",
  "name": "王医生3",
  "title": "主任",
  "headPic": "/headPic/wang",
  "descText": "擅长各种疑难杂症",
  "user": "wang2",
  "department": "超声科",
  "password": "123456",
  "callerList": "[{},{}]"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
   }
}

```
## 测试工作者数据源
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "testSource",
  "stationID": 2,
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "table" : "workers_import",
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
    "result": "success"
   }
}
```

##测试工作数据源配置
接口地址: http://192.168.17.187/hqueue/manager/worker

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "testSourceConfig",
  "stationID": 2,
  "DBType" : "mysql",
  "host": "192.168.17.184",
  "port": "3306",
  "charset" : "utf8",
  "user" : "root",
  "passwd" : "123456",
  "DBName" : "HisQueue",
  "table" : "workers_import",
  
  "aliasID" : "id",
  "aliasName":"name",
  "aliasTitle":"title",
  "aliasDepartment":"department",
  "aliasDescText":"descText",
  "aliasHeadPic" : ""
}
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "sql": "(SELECT id as id , name as name , title as title , department as department , descText as descText from workers_import) as workerView",
     "result": "success"
   }
}
```
## 验证一个工作者ID是否可用
接口地址: http://192.168.17.187/hqueue/manager/worker/

方法: POST

参数:

```
{
  "token": " safe action",
  "action" : "checkID",
  "stationID": 2,
  "id" : "D003"
}
```
返回内容:
```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
        "conflict": 0
   }
}
```
##上传工作者头像接口
nginx方法接口地址
http://192.168.17.187/headpicUpload
web.py方法接口地址
http://192.168.17.187/hqueue/manager/upload

方法: POST

参数:
```
upload filename stationID_workerID.jpg
```
返回内容:

```
{ 
   "errInfo": "none",
   "rescode": "200",
   "detail":{
     "result": "success",
     "upload_path" :"headpic/stationID2/D001.jpg",
     "size" : 100K,
   }
}

```
