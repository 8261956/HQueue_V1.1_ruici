#数据库

##访客数据源信息表

| name        | col           | val  |                        
| ------------- |:-------------:| -----:|                     
| 名称       		| name         |     XXX                  |
| 年龄       		| age         |     20                  |
| 队列           | queue          |      "US"              |
| 序号        | snumber         |     10             |
| 医保卡ID       	| id             |      "C02132311"      |
| 预约日期		 | orderDate        |   "20170102"                   |
| 预约时间		 | orderTime        |   "0820"                       |
| 登记日期       | registDate       |    "20170102"              |
| 登记时间       | registTime       |     "0820"              |
| 急诊   		  | emergency |  0           |
| 是否预约      | orderType | 1             |
| 医生ID      	| workerID      |  "D001"            |
| 医生姓名        | workerName         |  "王医生"                  |
| 科室        | department         |  “内科”                  |
| 病情描述        | descText    |  “肠胃不适”                  |
| 状态   			| status   |  "已预约"/“已登记”/“已就诊”       |

##工作者数据源信息表

| name        | col           | val  |    
| ------------- |:-------------:| -----:| 
| 工作者ID       | id         |  D001   |  
| 工作站ID       | stationID         |  S001   |  
| 用户名       | user         |  doctorWang   |  
| 密码       | password         |  123456   |  
| 工作者名称     | name       |  李医生  |  
| 工作者职称     | title| “教授”  |  
| 工作者科室       | department         |  内科 |  
| 工作者描述     | descText     | 擅长...  |
| 工作者头像	   |headPicPath| ftp:127.0.0.1/headpic|
| 可使用的叫号器	   |callerList| [{ID:"C1213",name:"内科1室"},{ID:"C1214",name:"内科2室"}],|

##工作站信息

| name        | col           | val  |                 
| ------------- |:-------------:| -----:|              
| 工作站ID      | id       |       string           |
| 工作站名称      | name       |       string           |
| 工作站描述      | descText           |  string           |
| 数据源类型      |  DBType  |     sql 2000             |
| 数据源地址      |  host  |     string             |
| 数据源端口      |  port  |     string             |
| 数据库字符集      |  charset |     string             |
| 数据源账户     |  user  |     string             |
| 数据库密码      |  passwd |     string             |
| 数据库库名      |  DBName  |     Keyspace1             |
| 数据库表名      |  tableName  |     Keyspace1             |
| 字段别名‘Name’   | aliasName          |    string              |
| 字段别名‘age’  |   aliasAge          |    string              |
| 字段别名'queue'    |  aliasQueue          |   string             |
| 字段别名‘ID’  | aliasID    |      string |
| 字段别名 | aliasOrderDate       |                  |
| 字段别名 | aliasOrderTime       |                  |
| 字段别名 | aliasRegistDate       |                  |
| 字段别名  | aliasRegistTime |                  |
| 字段别名 | aliasSnumber       |                  |
| 字段别名 | aliasVIP       |                  |
| 字段别名 | aliasOrderType       |                  |
| 字段别名 | aliasWorkerID       |                  |
| 字段别名  | aliasWorkerName |                  |
| 字段别名  | aliasDepartment |                  |
| 字段别名 | aliasDescText       |                  |
| 字段别名 | aliasStatus       |                  |
| 数据刷新周期      |  renewPeriod  |     5s             |
| 管理队列列表  | queueList   |         list      |
| 管理工作者列表  | workerList   |         list      |
| 管理呼叫器列表  | callerList   |         list      |

##呼叫器信息表
| name        | col           | val  |                 
| ------------- |:-------------:| -----:|              
| 呼叫器ID      | id       |       123          |
| 工作站ID      | stationID       |       2           |
| 呼叫器名称      | name       |       "李医生的呼叫器"           |
| 呼叫器IP      | ip      |      192.168.12.14          |
| 呼叫器类型      | type      |     soft/physic          |
| 呼叫器位置      | pos      |     “内科1号诊室”          |
| 可登录工作者     | workerLimit      |    none         |
| 优先呼叫队列ID      | priorQueue      |   "W001"     |

##队列信息列表
| name        | col           | val  |                 
| ------------- |:-------------:| -----:| 
| 队列ID       |       id           |int|   
| 分诊台ID       |       stationID           |int|    
| 队列名称Name       |       name           |string|
| 队列描述       |       descText           |string|
| 数据源过滤条件  | filter    |      'Queue = 'US'' |
| 队列使用模版 | scene       |       ‘normal’           |
| 队列是否需要本地激活| activeLocal       |       1           |
| 队列是否开放预约 | orderAllow       |      1          |
| 队列排序方式 | rankWay       |      string          |
| 该队列操作人员  | workerLimit |       list     |
|当前正在工作的人员|workerOnline|int|


##队列排队人员信息表
| name        | col           | val  |                 
| ------------- |:-------------:| -----:|              
| 日期     | date|       date    |
| 卡号ID     | visitorID|       string    |
| 主优先属性      | priorityVal           |    string              |
| 次优先属性     |  prioritySecVal          |   string            |
| 紧急     |  emergency          |   bool            |
| 老弱病残     |    weak  |   bool            |
| VIP     |    VIP  |   bool            |
| 排序          | order          |       int           |
| 移动路径          | Class            | list  |
| 已处理		|	done|	bool|
| 已移出		|	moved|	bool|
| 正在就诊		|  current|	bool|


##发布器参数表
| name        | col           | val  |                 
| ------------- |:-------------:| -----:|              
| 工作站ID     | stationID |       string    |
| 发布器ID     | publishID |       string    |
| 最大显示等候数     | cardID|       string    |
| 指定队列      | queue           |    list              |
| 显示工作人员信息     |  workerInfo          |   string     |



##日志信息记录
| name        | col           | val  |          
| ------------- |:-------------:| -----:|       
| 日志序号 | LogID          |                  |
| 日志时间 | Time           |                  |
|     工作站 | station        |                  |
| 日志级别 | Level          |                  |
| 日志操作 | Func           |                  |
| 日志内容 | Content        |      string     |


##账户管理表
| name        | col           | val  |          
| ------------- |:-------------:| -----:|       
| 账户ID     | accountID |       |              
| 账户名称   | name      |       |              
| 账户密码   | passwd    |       |              
| 账户类型、权限   | type      |Manager/Nurse/worker  | 
| 描述       | desc      |       |              
