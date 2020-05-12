# python-iotbot

```
IOTBOT SDK with python
```

## 简介

IOTBOT 是一个非常好用的 QQ 机器人框架，api 设计得也比较优雅，特别能用多种方式对接，跨平台也足够吸引人，所以花了点时间，对部分内容进行了封装，方便用 python 开发插件的朋友。

Tips: 因为本身只是对接口的封装，并没有什么实质性的亮点功能，（说白了就是体力活，）觉得还行可以 star 或者 fork 下来，添加更多功能（找人做体力活 😂)

## 安装

```bash
pip install python-iotbot
```

或者

```bash
git clone https://github.com/XiyaoWong/python-iotbot
cd python-iotbot
python setup.py install
```

或者

```bash
pip install git+https://github.com/XiyaoWong/python-iotbot.git@master
```

## 快速使用

```python
from iotbot import IOTBOT, GroupMsg

bot = IOTBOT(your_bot_qq)


@bot.on_group_msg
def group(ctx: GroupMsg):
    print(f"""
{ctx.FromNickName}在{ctx.MsgTime}的时候，发了一个类型是{ctx.MsgType}的消息，内容为：
{ctx.Content}""")
    print(ctx.get('CurrentQQ))


bot.run()
```

代码很简洁

要处理好友消息和事件都是一样的做法

```python
@bot.on_friend_msg
def friend(ctx: FriendMsg):
    pass


@bot.on_event
def event(message: dict):
    pass
```

其中**群消息**和**好友消息**中的`ctx`都是将原上报数据处理过的对象，你可以直接用`.`访问

事件类型暂时没有处理，因为用得比较少，为原来的字典类型

## 动作

其中封装了常见的几种方法（动作）用来发送消息

```python
from iotbot import Action

...
action = Action(qq) # action = Action(); action.bind_bot(bot)

# 发送好友消息
action.send_friend_text_msg(ctx.FromUin, '成功')
# 发送图片
action.send_friend_pic_msg(ctx.FromUin, picUrl='https://t.cn/A6Am7xYO', flashPic=True)
...

```

其中包括可选参数可自行设置

## 还是麻烦？

你会发现有几段代码都是固定的，创建机器人对象，写装饰器
所以你可以这样,在命令行中

```bash
$iotbot -n app -q 123456
# 或者
$iotbot
```

```
将创建app.py文件, 机器人QQ为：123456。是否确定？ y/N: y
创建成功~

执行如下命令：python app.py

在机器人所在的群或私聊机器人发送：.test
```

## Thx list

[golezi/pyiotqq](https://github.com/golezi/pyiotqq)

[mcoo/iotqq-plugins-demo](https://github.com/mcoo/iotqq-plugins-demo)

部分参考

## LICENSE

MIT
