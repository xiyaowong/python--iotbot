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
queue: 队列开关
queue_delay: 队列延时
------
timeout: 发送请求等待响应的时间
api_path:
port:
host:
'''
```

**每个方法有完善的代码提示，参数命名也对应原 api 数据命名，所以不说明了。对于参数的疑问请先查询 iotqq 提供 webapi 文档
如果还有疑问，请查看源码**

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

| 名称                     | 作用                                              |
| ------------------------ | ------------------------------------------------- |
| send_friend_text_msg     | 发送好友文本消息                                  |
| get_user_list            | 获取好友列表                                      |
| send_friend_voice_msg    | 发送好友语音消息                                  |
| send_friend_pic_msg      | 发送好友图片消息                                  |
| send_group_text_msg      | 发送群文字消息                                    |
| send_group_voice_msg     | 发送群语音                                        |
| send_group_pic_msg       | 发送群图片                                        |
| send_private_text_msg    | 发送私聊文字消息                                  |
| send_private_voice_msg   | 发送私聊语音                                      |
| send_private_pic_msg     | 发送私聊图片                                      |
| send_group_json_msg      | 发送群 Json 类型信息                              |
| send_group_xml_msg       | 发送群 Xml 类型信息                               |
| revoke_msg               | 撤回消息                                          |
| search_group             | 搜索群组                                          |
| get_user_info            | 获取用户信息                                      |
| get_cookies              | 获取 cookies                                      |
| get_group_list           | 获取群聊列表                                      |
| get_group_user_list      | 获取群成员列表                                    |
| get_group_admin_list     | 获取群管理列表                                    |
| get_group_all_admin_list | 获取包括群主在内的所有管理员列表                  |
| set_unique_title         | 设置群成员头衔                                    |
| modify_group_card        | 修改群名片                                        |
| refresh_keys             | 刷新 key 二次登陆, 成功返回 True， 失败返回 False |
| add_friend               | 添加好友                                          |
| deal_friend              | 处理好友请求                                      |
| all_shut_up_on           | 开启全员禁言                                      |
| all_shut_up_off          | 关闭全员禁言                                      |
| you_shut_up              | 群成员禁言                                        |
| like                     | 通用 call 点赞                                    |
| like_2                   | 点赞                                              |
| logout                   | 退出 qq                                           |
| get_login_qrcode         | 获取登录二维码的 base64 编码                      |
| get_friend_file          | 获取好友文件下载链接                              |
| get_group_file           | 获取群文件下载链接                                |
| set_group_announce       | 设置群公告                                        |
| set_group_admin          | 设置群管理员                                      |
| cancel_group_admin       | 取消群管理员                                      |
| repost_video_to_group    | 转发视频到群聊                                    |
| repost_video_to_friend   | 转发视频给好友                                    |

## 发送队列

发送过快会导致发送失败或消息被 tx 屏蔽, 所以某些情况很有必要开启，特别是发图

初始化`Action`时设置参数`queue`为`True`即可以队列的方式执行发送任务，开启后对应有两个参数可以设置

`queue_delay` 队列每一次发送之间的延时，一般保持默认即可，这是群内大佬的经验数值

**注意**:

1. 开启队列后方法都没有返回值，所以只适合执行发送任务。

(v2.4.0 增加)在使用开启队列的 action 运行各种方法时，可指定关键字参数`callback`,
callback 要求为一个函数，函数有且只能有一个参数，之后会自动将队列中任务的返回值传说 callback 执行

没有对不同的群和 api 进行分开发送，即所有操作都会排入队列中, 这样也符合真人行为(个人觉得)

2. Action 必须定义为**全局变量**，不能放在接收函数内,这个其实不应该说明的，因为放在函数内会导致的问题显而易见
3. 参考[bot_test_queue](https://github.com/XiyaoWong/python-iotbot/blob/master/sample/plugins/bot_test_queue.py)

## sugar

在 action 的基础上深度封装了常用操作, 适用于**简单**的场景，不支持队列发送
使用的前提是使用默认的端口和 ip 配置或者已经设置好文件`.iotbot.json`，这个是什么在配置章节介绍

```python
from iotbot.sugar import Text, Picture, Voice, Send

Text('Hello') # 对该消息的来源(群或好友),发送内容为Hello的文字消息
Picture(pic_url='') # 同上，这里是发送图片消息
Voice(...)
...
```

调用这几个方法，会自动选择上下文对进行不同的回复，包括临时会话

具体参数看代码提示, 如果提示不全请看源码注释!

这几个函数**只能**在群消息和好友消息接收函数中使用

## Tips

因为 Action 和 IOTBOT
实例完全解耦，所以你可以在自己的脚本中使用，比如用这个替代
shell 替代定时脚本
