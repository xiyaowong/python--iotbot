# 快速开始

```python
from iotbot import IOTBOT, Action, GroupMsg

bot = IOTBOT(123456)
action = Action(bot)


@bot.on_group_msg
def group(ctx: GroupMsg):
    if ctx.Content == 'test':
        action.send_group_text_msg(
            ctx.FromGroupId,
            'ok'
        )


if __name__ == "__main__":
    bot.run()
```
解释：假设iotbot的服务端配置都是默认即端口为8888。
1. 导入相关模块
2. 初始化机器人，qq为123456
3. 基于机器人实例初始化'动作实例'
4. 通过装饰器，注册group函数为一个群消息接收者
5. 检测内容，并执行发送动作
6. 启动
运行这几行代码，当你在群聊发送test后，机器人会回复ok
