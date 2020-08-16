# 其他说明

1. 主程序中注册的 receiver 函数优先级比插件中的高，也就是优先分发消息，但实际上他们时间的时间差可以忽略
2. 每个接收函数运行起来是独立的，彼此毫无关联

3. `utils`模块提供了一些辅助数据

```python
from iotbot import utils
```

`utils.MsgTypes`: 消息类型
`utils.EventNames`: 事件类型
`utils.Emoticons`: 表情代码
