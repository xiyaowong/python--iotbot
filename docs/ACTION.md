# 动作

```
这个类封装了大部分webapi, 并添加了部分常用方法
```

## 初始化

```python
from iotbot import Action

action = Action(123456)
'''
必选参数：
qq_or_bot: qq 号或者机器人实例(`IOTBOT`), 如果传入机器人实例，如果开启多Q，将选取第一个 QQ

可选参数:
与发送队列有关的参数:
queue:
queue_delay:
send_per_minute:
send_per_minute_behavior:
send_per_minute_callback:
------
timeout:
api_path:
port:
host:
'''
```

**每个方法有完善的代码提示，参数命名也对应原 api 数据命名，所以不说明了。对于参数的疑问请先查询 iotqq 提供 webapi 文档**

## Action.baseSender

所有方法调用这个基础方法

开放出来是因为有时候出了新功能，可以用这个自行构建请求。
参数：

- method: 请求方法, 如 POST、GET
- funcname: 请求类型, 即 iotbot webapi 路径中的参数
- data: post 的数据, 不需要就不传
- timeout: 发送请求等待响应的时间(requests)
- api_path: 默认为/v1/LuaApiCaller
- iot_timeout: IOT 端处理请求等待的时间, 即 iotbot webapi 路径中的参数, 具体意思自行去机器人框架了解
- bot_qq: 机器人 QQ

## 方法一览

**表格显示不出可以直接在 github 上看**

| 名称                   | 作用                                              |
| ---------------------- | ------------------------------------------------- |
| send_friend_text_msg   | 发送好友文本消息                                  |
| get_user_list          | 获取好友列表                                      |
| send_friend_voice_msg  | 发送好友语音消息                                  |
| send_friend_pic_msg    | 发送好友图片消息                                  |
| send_group_text_msg    | 发送群文字消息                                    |
| send_group_voice_msg   | 发送群语音                                        |
| send_group_pic_msg     | 发送群图片                                        |
| send_private_text_msg  | 发送私聊文字消息                                  |
| send_private_voice_msg | 发送私聊语音                                      |
| send_private_pic_msg   | 发送私聊图片                                      |
| send_group_json_msg    | 发送群 Json 类型信息                              |
| send_group_xml_msg     | 发送群 Xml 类型信息                               |
| revoke_msg             | 撤回消息                                          |
| search_group           | 搜索群组                                          |
| get_user_info          | 获取用户信息                                      |
| get_cookies            | 获取 cookies                                      |
| get_group_list         | 获取群聊列表                                      |
| get_group_user_list    | 获取群成员列表                                    |
| get_group_admin_list   | 获取群管理列表                                    |
| set_unique_title       | 设置群成员头衔                                    |
| modify_group_card      | 修改群名片                                        |
| refresh_keys           | 刷新 key 二次登陆, 成功返回 True， 失败返回 False |
| add_friend             | 添加好友                                          |
| deal_friend            | 处理好友请求                                      |
| all_shut_up_on         | 开启全员禁言                                      |
| all_shut_up_off        | 关闭全员禁言                                      |
| you_shut_up            | 群成员禁言                                        |
| like                   | 通用 call 点赞                                    |
| like_2                 | 点赞                                              |
| logout                 | 退出 qq                                           |
| get_login_qrcode       | 获取登录二维码的 base64 编码                      |
| get_friend_file        | 获取好友文件下载链接                              |
| get_group_file         | 获取群文件下载链接                                |
| set_group_announce     | 设置群公告                                        |

## 发送队列

发送过快会导致发送失败，或消息被 tx 屏蔽, 所以某些情况很有必要开启，特别是发图

初始化`Action`时设置参数`queue`为`True`即可以队列的方式执行发送任务，开启后对应有两个参数可以设置

`queue_delay` 队列每一次发送之间的延时，一般保持默认即可，这是群内大佬的经验数值

**注意**:

1. 开启队列后方法都没有返回值，所以只适合执行发送任务
2. Action 必须定义为**全局变量**，不能放在接收函数内
   参考[bot_test_queue](https://github.com/XiyaoWong/python-iotbot/blob/master/sample/plugins/bot_test_queue.py)

### 发送限额(每分钟)

可以设置每分钟允许最多发送多少条消息，因此只在**开启队列**后才有效
参数：

1. `send_per_minute` 每分钟发送多少条
2. `send_per_minute_behavior` 如果每分钟发送条数满了，该怎么处理队列剩余的任务，可选项有 ①`action.WAIT_THEN_RUN`等待至下一分钟，再继续执行剩余任务 ②`action.STOP_AND_DISCARD`删除剩余任务
3. 还有一个不太实用的参数`send_per_minute_callback`这个参数是一个函数，在每分钟发送条数满了之后自动调用，传给该函数的参数是一个元组 -> (剩余时间, 剩余任务数))

其他说明：发送限额因为某些原因不好实现针对不同群聊进行分开记录，所以假定有两个群同时发送同一个指令，每分钟限制会把这些消息统计在一起。可以通过定义和使用不同的 action 来解决...

## sugar

在 action 的基础上深度封装了常用操作

```python
from iotbot.sugar import Text, Picture, Voice

Text('Hello') # 对该消息的来源(群或好友),发送内容为Hello的文字消息
Picture(pic_url='') # 同上，这里是发送图片消息
Voice(...)
...
```

具体参数看代码提示即可

这几个函数**只能**在群消息和好友消息接收函数中使用

同时必须保证 iotbot 端的配置均为默认配置，即端口号为 8888

以后若有添加，不会在写在这里，更新后留意代码补全列表即可

## Tips

因为 Action 和 IOTBOT 实例完全解耦，用这个替代 shell 脚本执行定时任务，会很方便
