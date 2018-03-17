# 策略管理接口
## 添加自定义场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```
{
  "token": " safe action",
  "action": "addScene",
  "name": "测试",
  "activeLocal": "1",
  "rankWay": "registTime",
  "delayTime": "30",
  "waitNum": "5",
  "outputText": "就诊",
  "passedWaitNum": "5",
  "reviewWaitNum": "5",
  "priorNum": "3"
}
```

返回内容：

```
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success",
    "sceneID": "6"
  }
}
```

## 修改某一个场景

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```
{
  "token": " safe action",
  "action": "editScene",
  "sceneID": "9",
  "name": "测试",
  "activeLocal": "1",
  "rankWay": "registTime",
  "delayTime": "30",
  "waitNum": "5",
  "outputText": "取药",
  "passedWaitNum": "5",
  "reviewWaitNum": "5",
  "priorNum": "3"
}
```

返回内容：

```
{
  "errInfo": "none",
  "rescode": "200",
  "detail": {
    "result": "success"
  }
}
```

## 获取某一个场景的信息

接口地址： http://192.168.17.187/hqueue/manager/scene

方法： POST

参数：

```
{
    "token": " safe action",
	"action": "getSceneInfo",
	"sceneID": 9
}
```

返回内容：

```
{
    "errInfo": "none ",
    "rescode": "200",
    "detail": {
        "activeLocal": 1,
        "rankWay": "registTime",
        "waitNum": 5,
        "delayTime": 30,
        "name": "测试",
        "outputText": "就诊",
        "id": 9,
        "passedWaitNum": "5",
        "reviewWaitNum": "5",
        "priorNum": "3",
        "descText": "测试场景, 需要本地激活, 使用挂号时间进行排序, 播报请**到**就诊"
    }
}
```