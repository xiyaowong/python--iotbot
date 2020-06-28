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

- qq_or_bot: qq 号或者机器人实例(`IOTBOT`)
- timeout: 等待 IOTBOT 响应时间即`requests`请求中的 timeout, 之前是推荐设置很低，这样提高效率，但现在已经不用了
- log_file_path: 日志文件路径
- api_path: 默认是'`/v1/LuaApiCaller'`， 如需更改，注意前面的斜杆

**每个方法有完善的代码提示，参数命名也对应原 api 数据命名，所以不说明了。对于参数的疑问请先了解iotqq提供webapi文档**

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
| get_group_list         | 获取 cookies                                      |
| get_group_user_list    | 获取群成员列表                                    |
| set_unique_title       | 设置群成员头衔                                    |
| modify_group_card      | 修改群名片                                        |
| refresh_keys           | 刷新 key 二次登陆, 成功返回 True， 失败返回 False |
| add_friend             | 添加好友                                          |
| deal_friend            | 处理好友请求                                      |
| all_shut_up_on         | 开启全员禁言                                      |
| all_shut_up_off        | 关闭全员禁言                                      |
| you_shut_up            | 群成员禁言                                        |
