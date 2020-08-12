# python-iotbot

```
IOTBOT sync SDK with Python
```

## Install

```shell
pip install git+https://github.com/xiyaowong/python-iotbot.git@master
```

## Quick Start

```python
from iotbot import IOTBOT, GroupMsg

bot = IOTBOT(your_bot_qq)


@bot.on_group_msg
def group(ctx: GroupMsg):
    print(f"""
{ctx.FromNickName}在{ctx.MsgTime}的时候，发了一个类型是{ctx.MsgType}的消息，内容为：
{ctx.Content}""")
    print(ctx.CurrentQQ)


bot.run()
```

[documentation](https://python-iotbot.readthedocs.io/en/latest/ "documentation")

## LICENSE

MIT
