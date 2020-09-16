# 接收函数装饰器

这里提供了几个装饰器可快速管理接收函数，可用于快速构建简单的插件

## 作用一览

### not_botself

```python
def not_botself():
    """忽略机器人自身的消息"""
```

### is_botself

```python
def is_botself():
    """只要机器人自身的消息"""
```

### in_content

```python
def in_content(string: str):
    """
    接受消息content字段含有指定消息时, 不支持事件类型消息
    :param string: 支持正则
    """
```

### equal_content

```python
def equal_content(string: str):
    """
    content字段与指定消息相等时, 不支持事件类型消息
    """
```

### not_these_users

```python
def not_these_users(users: list):
"""仅接受这些人的消息
:param users: qq 号列表
"""
```

### only_these_users

```python
def only_these_users(users: list):
"""仅接受这些人的消息
:param users: qq 号列表
"""
```

### only_this_msg_type

```python
def only_this_msg_type(msg_type: str):
    """仅接受该类型消息
    :param msg_type: TextMsg, PicMsg, AtMsg, ReplyMsg, VoiceMsg之一
    """
```

### not_these_groups

```python
def not_these_groups(groups: list):
    """不接受这些群组的消息
    :param groups: 群号列表
    """
```

### only_these_groups

```python
def only_these_groups(groups: list):
    """只接受这些群组的消息
    :param groups: 群号列表
    """
```

```python
def startswith(string:str, trim=True):
    """content以指定前缀开头时
    :param string: 前缀字符串
    :param trim: 是否将原始Content部分替换为裁剪掉前缀的内容
    """
```

这里没写全，还是那句话，用的时候请看代码提示或查看源码

## 几个说明

1. in_content 与 equal_content
   有一点不同，in_content 用的是最原始的 Content 字段数据，比如图片消息是 json 格式的字符串；
   而 equal_content 使用的是将 json 格式数据解码后的 Content,
   `startswith`装饰器和`equal_content`一样
2. **对装饰器的具体行为有疑惑的请看源码**
3. **框架对艾特消息都没有处理，所以编写与艾特有关功能时请仔细考虑装饰器是否适用**

## 使用示例

`app.py`

```python
import iotbot.decorators as deco

... # 省略常规定义部分

@bot.on_group_msg
@deco.only_these_users([111, 222])
@deco.in_content('Hello')
def group1(ctx: GroupMsg): # 只有发送人qq是111或222，且包含Hello关键字时，才会被执行
    action.send_group_text_msg(
        ctx.FromGroupId,
        '测试指令 Hello'
)
```

`bot_test.py`

```python
from iotbot import Action, GroupMsg
import iotbot.decorators as deco


@deco.equal_content('测试')
@deco.only_these_groups([111])
def receive_group_msg(ctx: GroupMsg): # 仅当发送内容为'测试'且群号是111时，财被执行
    Action(ctx.CurrentQQ).send_group_text_msg(
        ctx.FromGroupId,
        '测试ok'
    )
```
