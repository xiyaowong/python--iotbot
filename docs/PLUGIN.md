# 插件化

## 启用

要开启插件功能，只需在定义机器人时设置对应参数。

```python
from iotbot import IOTBOT, GroupMsg

bot = IOTBOT(your_bot_qq, use_plugins=True)
# 参数`plugin_dir`用来指定插件所在文件夹, 默认为`plugins`,
# 不是路径，必须是在同目录下的一个文件夹
# 强烈建议默认，第一方面少坑，第二如果不使用默认，在很多方法下，需要手动传参，很麻烦
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

插件由一个插件管理器对象管理

假设 `bot = IOTBOT(123)`

可以通过以下方法管理插件:

1. 方法`bot.reload_plugins()` 重载旧插件，加载新插件
2. 属性`bot.plugins` 获取插件名称列表，用于下面方法
3. 方法`bot.reload_plugin(plugin_name)` 根据插件名重载对应插件
4. 方法`bot.refresh_plugins()` 刷新插件目录所有插件
5. 方法`bot.load_plugins()` 加载新插件，已加载插件不会重载

以上方法是插件管理对象方法的快捷方式，也是**唯一推荐**的几个方法，如果你想更细致的管理插件，看下面：

直接调用 `bot.plugMgr` 的方法或属性

1. `load_plugins()` 加载插件，不会重载，可指定参数 plugin_dir，如果该插件位于已停用插件列表，也不会被加载
2. `refresh()` 刷新插件目录所有插件
3. `reload_plugins()` 重载旧插件，加载新插件。 可指定参数 plugin_dir
4. `reload_plugin()` 根据插件名重载对应插件
5. `remove_plugin()` 根据插件名停用对应插件
6. `recover_plugin()` 与 remove 对应，根据插件名恢复使用对应插件
7. `plugins` 获取已启用插件名称的列表
8. `removed_plugins` 获取已停用插件名称的列表

因为停用的插件列表是保存在内存中的，重启程序后就没了。推荐自己用其他方式实现
