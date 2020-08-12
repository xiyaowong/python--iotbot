# 客户端(IOTBOT)

## 初始化

```python
from iotbot import IOTBOT

bot = IOTBOT(123456)
'''
必选参数:
qq:  机器人QQ号, 多Q传入列表即可

可选参数:
ues_plugins: 是否开启插件功能
plugin_dir: 插件目录(同级目录)
group_blacklist: 群黑名单, 此名单中的群聊消息不会被处理,默认为空
friend_whitelist: 好友黑名单，此名单中的群聊消息不会被处理,默认为空
log: 是否开启log, ×这块没写好，日志功能很糟糕×现已用三方库替代，稍微好一点点了
log_file: 是否输出日志文件
port: bot端运行端口
host: bot端运行ip，需要包含schema
beat_delay: 心跳频率，单位秒
'''
```

## 注册接收函数

在收到服务端消息后，首先将原始消息进行包装，然后将包装后的消息(后称上下文 ctx)作为参数传入每个消息接受函数(receiver)自动调用

### 通过方法添加接收函数

- `bot.add_group_msg_receiver(func)` 群消息接收函数
- `bot.add_friend_msg_receiver(func)` 好友消息接收函数
- `bot.add_event_receiver(func)` 事件消息接收函数

func 是对应的接收函数, 有自己编写，参数唯一，均为对应消息类型的**上下文对象**

### 通过装饰器添加接收函数

- @bot.on_group_msg # 群消息
- @bot.on_friend_msg # 好友消息
- @bot.on_event # 事件消息

装饰器本质是调用的方法。

**接收函数数量和命名都不受限制**

### 通过插件添加接收函数

在插件部分说明

## 消息上下文对象

接收函数必须有且只有一个参数，这个参数是消息上下文(后面用 ctx 代替)，是将服务端传过来的原始信息处理后的对象。
原始数据是一个字典, 经过包装得到的 ctx 各项属性是原始数据中常用的字段，如果你想使用原始数据，`ctx.message`即
是原始数据

在编写接收函数时,建议导入相关类(FriendMsg, GroupMsg, EventMsg)，使用注解语法，这样可以获得足够的代码提示

## 消息中间件

可以对每一个(三个)消息上下文注册且只能一个中间件函数，中间件函数签名与接收函数一致。
中间件的返回值如果与 ctx 类型一致，则将该返回值作为接收函数的参数
中间件的主要适用于给 ctx 添加额外属性，用于在接收函数中通过参数 ctx 直接访问，这对编写插件会有帮助

比如给 ctx 添加 master 属性(主人 qq)，这样从而可以从插件中访问，而不用显式的注明主人 QQ 号、可以给 ctx 添加开启队列的 Action，这样所有插件共用同一个队列

## 提取准确信息的 refine 函数

默认传递的上下文对象只包含该消息的固定字段，也就是不管哪种，都会包含的东东。
一般情况下，对于群消息和好友消息的接收是够了的，但是有时候需要提取图片数据，语音，或者红包数据时，
会有很多不同的字段，需要自己解码 json。同样，对于群和好友消息来说这都还好，但是对于**事件**消息,
有很多不同的字段，如果要做这方面的功能，会比较麻烦。

为了避免重复劳动，提供了一系列 `refine_?` 函数用来进一步解析数据。

```python
from iotbot.refine_message import *
# 按需导入
```

其中每一个函数对应一种消息类型，如果消息类型与该函数所期望处理的类型一致, 则会返回一个新的上下文对象
新对象中包含了更详尽的属性。
如果消息类型不匹配，则返回 None，所以 refine 函数也能起判断(类型筛选)的作用

通过函数名称自行选择所需的函数

参考示例: [bot_test_refine_funcs.py](https://github.com/XiyaoWong/python-iotbot/blob/master/sample/plugins/bot_test_refine_funcs.py)

### 一览

| 名称                                  | 作用                |
| ------------------------------------- | ------------------- |
| refine_group_revoke_event_msg         | 群成员撤回消息事件  |
| refine_group_exit_event_msg           | 群成员退出群聊事件  |
| refine_group_join_event_msg           | 某人进群事件        |
| refine_friend_revoke_event_msg        | 好友撤回消息事件    |
| refine_friend_delete_event_msg        | 删除好友事件        |
| refine_group_adminsysnotify_event_msg | 加群申请            |
| refine_group_shut_event_msg           | 群禁言事件          |
| refine_group_admin_event_msg          | 管理员变更事件      |
| refine_voice_group_msg                | 群语音消息          |
| refine_pic_group_msg                  | 群图片/表情包消息   |
| refine_RedBag_group_msg               | 群红包消息          |
| refine_voice_friend_msg               | 好友语音消息        |
| refine_pic_friend_msg                 | 好友图片/表情包消息 |
| refine_RedBag_friend_msg              | 好友红包消息        |

## 客户端属性或方法

- `IOTBOT.receivers` 属性，三种消息接收函数数量
  还有一系列与插件有关的方法，后面插件部分再说明

---

**注意不要中途尝试修改属性**
