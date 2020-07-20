```
因为错误的改了github用户名，导致之前的python-iotbot仓库名不能使用了。所以没办法只能中间多加一个 【-】
除了github上的仓库名改了之外，其他内容一律没变。
注意一下。。。:(

```
# python-iotbot

```
IOTBOT SDK with python
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
    print(ctx.get('CurrentQQ'))


bot.run()
```
[documentation](https://python-iotbot.readthedocs.io/en/latest/ "documentation")

## LICENSE

MIT
