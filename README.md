# python-iotbot

[![pypi](https://img.shields.io/pypi/v/python-iotbot?style=flat-square 'pypi')](https://pypi.org/project/python-iotbot/)

## Install

```shell
pip install python-iotbot -i https://pypi.org/simple --upgrade
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

[documentation](https://python-iotbot.readthedocs.io/en/latest/ 'documentation')

## LICENSE

MIT
