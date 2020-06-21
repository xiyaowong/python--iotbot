# 客户端(IOTBOT)

## 初始化

```python
from iotbot import IOTBOT

bot = IOTBOT(123456)
```
参数:
* qq: 机器人QQ号(必选)
* use_plugins: 是否开启插件功能
* plugin_dir: 插件存放目录
* group_blacklist: 群黑名单, 此名单中的群聊消息不会被处理,默认为空，即全部处理
* friend_whitelist: 好友白名单，只有此名单中的好友消息才会被处理，默认为空，即全部处理
* log: 是否开启log
* log_file_path: 日志文件路径
* port: 运行端口
* beat_delay: 心跳延时时间（s）
* host: ip，需要包含协议

到时候用的时候，IDE或编辑器会提示的，没什么好讲的地方。。。

## 注册接收函数
在收到服务端消息后，会将消息作为参数传入每个消息接受函数(receiver)执行，但是不同于绑定

### 通过方法
* bot.add_group_msg_receiver(func)  # 群消息
* bot.add_friend_msg_receiver(func)  # 好友消息
* bot.add_event_receiver(func) # 事件消息

func是对应的接收函数

### 通过装饰器
* @bot.on_group_msg  # 群消息
* @bot.on_friend_msg  # 好友消息
* @bot.on_event  # 事件消息

装饰器本质是调用的方法。

**接收函数数量为0个或无限多个, 函数名也随意**

## 消息上下文
接收函数必须有且只有一个参数，这个参数是消息上下文(后面用ctx代替)，是将服务端传入信息处理后的对象。
原始数据是一个字典, ctx的各项属性是原始数据的**固定字段**，其中ctx.message即是原始数据。

注意事件消息ctx还是原始字典。(具体用的时候，打印出来分析即可)

建议导入相关类(FriendMsg, GroupMsg)，使用注解语法，这样可以获得足够的代码提示

## 客户端属性或方法
* `IOTBOT.receivers` 属性，三种消息接收函数数量
* `IOTBOT.refresh_plugins` 方法, 刷新插件，后面插件部分会讲

---

**注意不要中途修改属性**
