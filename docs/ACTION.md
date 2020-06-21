# 动作

```
这个类封装了大部分IOTBOT webapi
```

## 初始化
```python
from iotbot import Action

action = Action(123456)
```
简单说明几个参数
* qq_or_bot: qq号或者机器人实例(`IOTBOT`)
* timeout: 等待IOTBOT响应时间即`requests`请求中的timeout, 之前是推荐设置很低，这样提高效率，但现在已经不用了
* log_file_path: 日志文件路径
* api_path: 默认是'`/v1/LuaApiCaller'`， 如需更改，注意前面的斜杆

**每个方法有完善的代码提示，参数命名也对应原api数据命名，所以不说明了。**

## Action.baseSender
所有方法调用这个基础方法

开放出来是因为有时候出了新功能，可以用这个自行构建请求。
参数：
* method: 请求方法, 如POST、GET
* funcname: 请求类型, 即iotbot webapi路径中的参数
* data: post的数据, 不需要就不传
* timeout: 发送请求等待响应的时间(requests)
* api_path: 默认为/v1/LuaApiCaller
* iot_timeout: IOT端处理请求等待的时间, 即iotbot webapi路径中的参数, 具体意思自行去机器人框架了解
* bot_qq: 机器人QQ
