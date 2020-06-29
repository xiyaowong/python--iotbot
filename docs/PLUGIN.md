# 插件化

## 启用

要开启插件功能，只需在定义机器人时设置对应参数。

```python
from iotbot import IOTBOT, GroupMsg

bot = IOTBOT(your_bot_qq, use_plugins=True)
# 参数`plugin_dir`用来指定插件所在文件夹, 默认为`plugins`,
# 不是路径，必须是在同目录下的一个文件夹
```

## 插件要求

1. 文件名需以`bot_`开头。这样做是因为考虑到会有一些模块需要导入，这样稍微快一点
2. 消息接收函数命名

   - receive_group_msg # 群消息
   - receive_friend_msg # 好友消息
   - receive_events # 事件消息

   命名错误不会影响程序运行，只是不会被使用。

3. 参数有且只有一个，即和前面主程序中写法一样

## 刷新插件

调用`IOTBOT.refresh_plugins`方法即可。
