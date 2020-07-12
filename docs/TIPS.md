# TIPS

因为考虑到有的机器人运行配置不同，比如默认的端口是 8888

每个插件都需要注明一点会很麻烦，而且`sugar`函数无法使用

所以新增部分配置会优先从环境变量中读取
目前可设置的值:

1. `IOTBOT_PORT` 端口号， 示例：`8888`
2. `IOTBOT_HOST` ip, 示例: `http://127.0.0.1`

可以这样做:

1. 安装`python-dotenv`库 -> `pip install python-dotenv`
2. 在你的项目根目录下创建 `.env`文件:
   ```ini
   IOTBOT_PORT = 8888
   IOTBOT_HOST = 'http://127.0.0.1'
   ```
