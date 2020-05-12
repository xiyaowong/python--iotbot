import sys
import time
from functools import wraps

import socketio

from .model import model_map


def _deco_creater(bind_type):
    def deco(self, func):
        @wraps(func)
        def wrapper(context):
            if not bind_type == 'OnEvents':  # 暂不支持event
                context = model_map[bind_type](context)
            return func(context)
        self.socketio.on(bind_type)(wrapper)
        return wrapper
    return deco


class IOTBOT:
    """
    :param qq: 机器人QQ号
    :param port: 运行端口
    :param beat_delay: 心跳延时时间（s）
    :param host: ip，需要包含协议
    """

    def __init__(self, qq: str, port=8888, beat_delay=60, host='http://127.0.0.1'):
        self.qq = str(qq)
        self.host = host
        self.port = port
        self.beat_delay = beat_delay

        self.__initialize_socketio()

    def run(self):
        try:
            self.socketio.connect(f'{self.host}:{self.port}', transports=['websocket'])
            self.socketio.wait()
        except Exception:
            sys.stdout.write('启动失败，请检查是否已启动IOTBOT。。。')
            sys.exit(1)

    def connect(self):
        print('Connected to server successfully!')
        while True:
            self.socketio.emit('GetWebConn', self.qq)
            time.sleep(self.beat_delay)

    def __initialize_socketio(self):
        self.socketio = socketio.Client()
        self.socketio.event()(self.connect)

    on_group_msg = _deco_creater('OnGroupMsgs')
    on_friend_msg = _deco_creater('OnFriendMsgs')
    on_event = _deco_creater('OnEvents')
