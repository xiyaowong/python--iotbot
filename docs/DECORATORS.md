# 接收函数装饰器

这里提供了几个装饰器可快速管理接收函数，可用于快速构建简单的插件

## 作用一览

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
     :param users: qq号列表
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
