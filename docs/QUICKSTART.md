# 快速开始

```python
from iotbot import IOTBOT, Action, GroupMsg

bot = IOTBOT(123456) # 实例化机器人
action = Action(bot) # 实例化发送动作，用于调用webapi, 这是传入bot实例是一个语法糖
# 实际的Action和IOTBOT完全解耦
# 以上实例参数均采用默认值，后续说明


@bot.on_group_msg # 通过装饰器, 注册group函数为一个群消息接收者
def group(ctx: GroupMsg):
    # 现在你可以在该函数编写逻辑了，每次有新的群消息，该函数被自动调用
    # 参数有且只有一个，即将原始数据包装过后的新的对象
    # 使用注解语法可以方便的获取各项数据
    if ctx.Content == 'test': # 如果发送的内容是 test 则对应回复 ok
        action.send_group_text_msg(
            ctx.FromGroupId,
            'ok'
        )


if __name__ == "__main__":
    bot.run()
```

这是一个最小实例，你可以再其中编写任意多的逻辑，依然不用担心效率问题
