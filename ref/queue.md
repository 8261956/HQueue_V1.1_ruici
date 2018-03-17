#工作站管理队列的接口

## 获取队列列表
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getList",
    "stationID" : 2
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 1,
    "list": [
      {
        "activeLocal": 0,
        "orderAllow": 1,
        "filter": "queue=men",
        "name": "队列1",
        "scene": "normal",
        "descText": "李医生的门诊队列",
        "stationID": 2,
        "workerLimit": ["D002", "1"],
        "workerOnline": null,
        "id": 0
      }
    ]
  }
}
```
## 获取队列配置信息
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getInfo",
    "stationID" : 2,
    "id" : 1
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "activeLocal": 0,
    "orderAllow": 1,
    "name": "队列1",
    "stationID": 2,
    "sceneID": 3,
    "scene": "normal",
    "descText": "李医生的门诊队列",
    "filter": "queue=men",
    "workerLimit": ["D002", "1"],
    "workerOnline": null,
    "id": 1
  }
}
```

## 添加一个队列
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "add",
    "stationID" : 2,
    "name": "队列2",
    "scene": "normal",
    "sceneID": 1,
    "descText": "李医生的门诊队列",
    "fliter": "queue=men",
    "workerLimit": ["D002", "1"]
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {}
}
```
## 删除一个队列
接口地址: http://hit.clear.cn/manager/delSqueue/S001

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "delete",
    "stationID" : 2,
    "id" : 3
}
```
返回内容:
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

## 修改一个队列配置
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:

```
{
    "token": " safe action",
    "action" : "edit",
    "stationID" : 2,
    "id" : 3,
    "name": "队列3",
    "scene": "normal",
    "sceneID": 1,
    "descText": "李医生的门诊队列",
    "filter": "queue=men",
    "workerLimit": ["D002", "1"]
}
```

返回内容

```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {}
}
```

## 获取数据源队列列表
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getSourceQueueList",
    "stationID" : 2
}
```
返回内容:
```
{ 
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 2,
    "list": [
      "AM",
      "PM"
    ]
  }
}
```
## 获取队列场景列表
接口地址: http://192.168.17.187/hqueue/manager/queueInfo

方法: POST

参数:
```
{
    "token": " safe action",
    "action" : "getSceneSupportList",
    "stationID" : 2
}
```
返回内容：
```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "num": 4,
    "list": [
      {
        "id": 1,
        "descText": "常规场景，不需要本地激活，开放预约，使用登记时间进行排序，播报请**到**就诊",
        "name": "常规"
      },
      {
        "id": 2,
        "descText": "常规场景，不需要本地激活，开放预约，使用登记时间进行排序,预约与普通按31比例分布，播报请**到**就诊",
        "name": "智能"
      },
      {
        "id": 3,
        "descText": "常规场景，不需要本地激活，开放预约，使用序号进行排序,预约与普通按31比例分布，播报请**到**就诊",
        "name": "序号"
      },
      {
        "id": 4,
        "descText": "药房场景，不需要本地激活，不开放预约，使用号码进行排序，播报请**到**取药",
        "name": "药房"
      }
    ]
  }
}

```

## 获取队列平均等待时间

接口地址：http://192.168.17.187/hqueue/manager/queueInfo

方法：POST

参数：

```
{
  "action": "getAvgWaitTime",
  "stationID": "49",
  "queueID": "51"
}
```

返回内容：

```
{
  "errInfo": "none ",
  "rescode": "200",
  "detail": {
    "queueID": "51",
    "stationID": "49",
    "avgWaitTime": "33.0"
  }
}
```