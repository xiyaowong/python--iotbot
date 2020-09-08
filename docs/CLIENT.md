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
'''
```

## 注册接收函数

在收到服务端消息后，首先将原始消息进行包装，然后将包装后的消息(后称上下文 ctx)作为参数传入每个消息接受函数(receiver)自动调用

### 通过方法添加接收函数

- `bot.add_group_msg_receiver(func)` 添加群消息接收函数
- `bot.add_friend_msg_receiver(func)` 添加好友消息接收函数
- `bot.add_event_receiver(func)` 添加事件消息接收函数

func 是对应的接收函数, 有自己编写，参数唯一，均为对应消息类型的**上下文对象**

### 通过装饰器添加接收函数

- @bot.on_group_msg # 群消息
- @bot.on_friend_msg # 好友消息
- @bot.on_event # 事件消息

装饰器是调用上面的方法

**接收函数数量和命名都不受限制**你可以针对不同的功能使用不同的接收函数

### 通过插件添加接收函数

在插件部分说明

## 消息上下文对象

接收函数必须有且只有一个参数，这个参数是消息上下文(后面用 ctx 代替)，是将服务端传过来的原始信息处理后的对象。
原始数据是一个字典, 经过包装得到的 ctx 各项属性是原始数据中常用的字段，什么是常用字段？就是每一个该类消息都具有的字段，
比如群消息中分有图片、文本、语音等，它们都有 FromGroupId、FromUserId 等字段，而它们的不同是在 Content 字段中
当然如果你想使用最原始的数据，使用`ctx.message`属性即可

在编写接收函数时,建议导入相关类(FriendMsg, GroupMsg, EventMsg)，使用注解语法，这样可以获得足够的代码提示, 也能避免出错

### 临时会话(私聊)消息

这是处理起来最麻烦的类型，所以框架没有提供处理，因为会特别乱
私聊消息属于好友消息一类，所以要在好友消息接收函数中处理,
如果 ctx.TempUin 属性不为 None，说明是私聊消息，可以通过 ctx.MsgType 和 ctx.TempUin 进行判断
ctx.TempUin 是发起该临时会话的入口群聊的 id, 其他的数据请自行处理

## 消息中间件

可以对每一个(三个)消息上下文注册且只能一个中间件函数，中间件函数签名与接收函数一致。
在中间件中，你可以对消息上下文进行修改，只建议添加属性，不破坏原始属性
中间件的返回值如果与 ctx 类型一致，则将该返回值作为接收函数的参数

中间件的主要适用于给 ctx 添加额外属性，用于在接收函数中通过参数 ctx 直接访问，这对编写插件会有帮助

比如给 ctx 添加 master 属性(主人 qq)，这样从而可以从插件中访问，而不用在每个需要用到的地方都显式的注明主人 QQ 号、
也可以给 ctx 添加开启队列的 Action，这样所有插件共用同一个队列等等

## 提取准确信息的 refine 函数

默认传递的上下文对象只包含该消息的固定字段，也就是不管哪种，都会包含的东东。
上面说过图片、文字、语音甚至红包消息等消息的不同在 Content 字段中，该字段永远是 str 类型，对于文本消息，该字段就是消息原文，
对其他消息来说，该字段是一个 json 格式的映射，如果需要处理这些数据，就需要自己通过解码 json 获得，
提取这些数据，如果是好友和群消息，不会特别麻烦，但如果处理含有特别多不同字段的事件类型的消息那就....
很明显这是一个常用操作，为了避免重复劳动，所以提供了一系列 `refine_?` 函数用来进一步解析数据。

refine
函数位于库的`refine_message`模块中,**现在是 refine 模块，refine_message 还可用，但之后可能取消删除**

```python
from iotbot.refine import *
# 按需导入
```

其中每一个函数对应一种消息类型或场景，如果消息类型与该函数所期望处理的类型一致,
则会返回一个新的上下文对象,新对象包含了更详尽的属性。
如果消息类型不匹配，则返回 None，所以 refine 函数也能起判断(类型筛选)的作用

通过函数名称自行选择所需的函数

请看示例: [bot_test_refine_funcs.py](https://github.com/XiyaoWong/python-iotbot/blob/master/sample/plugins/bot_test_refine_funcs.py)

### 一览

| 名称                                  | 作用                                |
| ------------------------------------- | ----------------------------------- |
| refine_group_revoke_event_msg         | 群成员撤回消息事件                  |
| refine_group_exit_event_msg           | 群成员退出群聊事件                  |
| refine_group_join_event_msg           | 某人进群事件                        |
| refine_friend_revoke_event_msg        | 好友撤回消息事件                    |
| refine_friend_delete_event_msg        | 删除好友事件                        |
| refine_group_adminsysnotify_event_msg | QQ 群系统消息通知(加群申请在这里面) |
| refine_group_shut_event_msg           | 群禁言事件                          |
| refine_group_admin_event_msg          | 管理员变更事件                      |
| refine_voice_group_msg                | 群语音消息                          |
| refine_video_group_msg                | 群视频消息                          |
| refine_pic_group_msg                  | 群图片/表情包消息                   |
| refine_RedBag_group_msg               | 群红包消息                          |
| refine_voice_friend_msg               | 好友语音消息                        |
| refine_video_friend_msg               | 好友视频消息                        |
| refine_pic_friend_msg                 | 好友图片/表情包消息                 |
| refine_RedBag_friend_msg              | 好友红包消息                        |

图片消息，与语音消息不同的是，因为可以同是发送几张图片，也就是富文本消息，其中的 GroupPic 是一个列表，
列表中是图片对象，图片对象又对应其数据

## 客户端属性或方法

- `IOTBOT.receivers` 属性，三种消息接收函数数量

  还有一系列与插件有关的方法，后面插件部分再说明

---

**注意不要中途尝试修改属性**
