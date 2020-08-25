# 定时任务

**并不推荐使用**

定时任务使用[schedule](https://pypi.python.org/pypi/schedule)库实现, 通过`IOTBOT`对象的`scheduler`属性访问

定义任务的方法与这个库一致，所以请看该库的文档

与之不同的是，你只需要定义任务，无需其他的操作，使用示例:

```python
from iotbot import IOTBOT

bot  = IOTBOT(123)

def hello():
    print('Hello')

def world():
    print('world')

bot.scheduler.every(20).seconds.do(hello) # 20s执行一次hello
bot.scheduler.every(10).seconds.do(world) # 10s执行一次world
```

不要调用`run_all`, `run_padding` 等方法
