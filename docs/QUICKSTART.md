# 快速开始

框架的基本思路就是通过 websocket(socketio)接收机器人服务端传来的各类消息和事件，通过调用 webapi
进行主动操作(发消息，获取数据等)。框架分为 client(客户端)和 action(动作)两部分，client 负责接收,在收到服务端传来的数据后,
将该数据进行一系列的包装使其变得更数据更直观，更易用，减少踩坑；action 负责发送(其他操作这里统称发送)，这部分主要是对
webapi 的封装，细化了部分 api 的使用，方法命名与其意思一致，参数名和作用与 webapi 一致，还有一些封装后面再说明.

例:

```python
from iotbot import IOTBOT, Action, GroupMsg

bot = IOTBOT(123456) # 传入QQ号实例化机器人
action = Action(bot) # 实例化发送动作，用于调用webapi, 这是传入bot实例, 也可以传入QQ号
# Action和IOTBOT完全解耦
# IOTBOT和Action都有若干个可选参数，以上实例是采用默认配置
# 常用的参数有host和port，后续再说明

# 通过装饰器, 注册group函数为一个群消息接收函数
@bot.on_group_msg
def group(ctx: GroupMsg):
    # 函数命名随意, 要求是参数有且只有一个，即将原始数据包装过后的新的对象
    # 使用注解语法可以方便的获取各项数据
    # 现在你可以在该函数编写逻辑了，每次有新的群消息，该函数被自动调用
    if ctx.Content == 'test': # 如果发送的内容是 test 则向该群发送文本 ok
        action.send_group_text_msg(
            ctx.FromGroupId,
            'ok'
        )


if __name__ == "__main__":
    bot.run() # 启动
```

这是一个最小实例，你可以在每个接收函数中编写任意多的逻辑，依然不用担心效率问题
