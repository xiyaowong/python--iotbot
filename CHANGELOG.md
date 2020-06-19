## CHANGELOG

### 0.2.3 - 2020-05-15

1. 更多action

2. 每个action除默认参数外，还可设置:
	- `api_path` `default=/v1/LuaApiCaller`
	- `iot_timeout`  `default=self.timeout=10` IOTBOT端处理允许等待的时间
    - `bot_qq`  `default=self.qq` 机器人QQ号

### 1.0.0 - 2020-05-28

#### 大改动
1. 插件化
2. 效率更高，不漏消息
3. 更多快捷方法
4. 更多自定义参数

### 1.1.0 - 2020-06-19
1. 无需重启即可更新插件，正常调用`refresh_plugins`方法即可
2. 改了下刷新插件后的显示信息
3. 增加刷新key二次登陆Action
4. 改善了生成模板
