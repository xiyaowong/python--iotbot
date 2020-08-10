# pylint: disable = too-many-instance-attributes
import copy
import logging
import os
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from typing import List
from typing import Union

import socketio

from .config import config
from .logger import Logger
from .model import EventMsg
from .model import FriendMsg
from .model import GroupMsg
from .model import model_map
from .plugin import PluginManager
from .typing import EventMsgReceiver
from .typing import FriendMsgReceiver
from .typing import GroupMsgReceiver


def _deco_creater(bind_type):
    def deco(self, func):
        if bind_type == 'OnGroupMsgs':
            self.add_group_msg_receiver(func)
        elif bind_type == 'OnFriendMsgs':
            self.add_friend_msg_receiver(func)
        else:
            self.add_event_receiver(func)
    return deco


class IOTBOT:
    """
    :param qq: 机器人QQ号(多Q就传qq号列表)
    :param use_plugins: 是否开启插件功能
    :param plugin_dir: 插件存放目录
    :param group_blacklist: 群黑名单, 此名单中的群聊消息不会被处理,默认为空，即全部处理
    :param friend_whitelist: 好友白名单，只有此名单中的好友消息才会被处理，默认为空，即全部处理
    :param log: 是否开启日志
    :param log_file_path: 日志文件路径
    :param port: 运行端口
    :param beat_delay: 心跳延时时间（s）
    :param host: ip，需要包含schema
    """

    def __init__(self,
                 qq: Union[int, List[int]],
                 use_plugins: bool = False,
                 plugin_dir: str = 'plugins',
                 group_blacklist: List[int] = None,
                 friend_blacklist: List[int] = None,
                 log: bool = True,
                 log_file_path: str = None,
                 port: int = 8888,
                 beat_delay: int = 60,
                 host: str = 'http://127.0.0.1'):
        if isinstance(qq, Sequence):
            self.qq = list(qq)
        else:
            os.environ['SINGLE_BOTQQ'] = str(qq)
            self.qq = [qq]
        self.use_plugins = use_plugins
        self.plugin_dir = plugin_dir
        self.host = config.host or host
        self.port = config.port or port
        self.beat_delay = beat_delay
        self.logger = Logger(log_file_path)
        if not log:
            logging.disable()
        self.group_blacklist = set(config.group_blacklist or group_blacklist or [])
        self.friend_blacklist = set(config.friend_blacklist or friend_blacklist or [])

        # 手动添加的消息接收函数
        self.__friend_msg_receivers_from_hand = []
        self.__group_msg_receivers_from_hand = []
        self.__event_receivers_from_hand = []

        # webhook 里的消息接收函数，是特例
        if config.webhook:
            from . import webhook
            # 直接加载进 `hand`
            self.__friend_msg_receivers_from_hand.append(webhook.receive_friend_msg)
            self.__group_msg_receivers_from_hand.append(webhook.receive_group_msg)
            self.__event_receivers_from_hand.append(webhook.receive_events)

        # 消息上下文对象中间件
        self.__friend_context_middleware: Callable[[FriendMsg], FriendMsg] = None
        self.__group_context_middleware: Callable[[GroupMsg], GroupMsg] = None
        self.__event_context_middleware: Callable[[EventMsg], EventMsg] = None

        # 插件管理
        self.plugMgr = PluginManager(self.plugin_dir)
        if use_plugins:
            self.plugMgr.load_plugins()
            print(self.plugMgr.info_table)

        # 初始化各项配置
        self.__initialize_socketio()
        self.__refresh_executor()
        self.__initialize_handlers()

    ########################################################################
    # shortcuts to call plugin manager methods
    ########################################################################
    # 只推荐使用这几个方法，其他的更细致的方法需要通过 plugMgr 对象访问
    def load_plugins(self):
        '''加载新插件'''
        self.plugMgr.load_plugins()

    def reload_plugins(self):
        '''重载旧插件，加载新插件'''
        self.plugMgr.reload_plugins()

    def reload_plugin(self, plugin_name: str):
        '''重载指定插件'''
        self.plugMgr.reload_plugin(plugin_name)

    def refresh_plugins(self):
        '''刷新插件目录所有插件'''
        self.plugMgr.refresh()
        print(self.plugMgr.info_table)

    @property
    def plugins(self):
        '''插件名列表'''
        return self.plugMgr.plugins
    ########################################################################

    def run(self):
        self.logger.info('Connecting to the server...')

        try:
            self.socketio.connect(f'{self.host}:{self.port}', transports=['websocket'])
        except Exception as e:
            self.logger.error(f'启动失败 -> {e}')
            sys.exit(1)
        else:
            try:
                self.socketio.wait()
            except KeyboardInterrupt:
                self.__executor.shutdown(wait=False)
                sys.exit(0)

    def connect(self):
        self.logger.info('Connected to server successfully!')
        while True:
            for qq in self.qq:
                self.socketio.emit('GetWebConn', str(qq))
            time.sleep(self.beat_delay)

    @property
    def receivers(self):
        '''消息处理函数数量'''
        return {
            'friend': len((*self.plugMgr.friend_msg_receivers,
                           *self.__friend_msg_receivers_from_hand)),
            'group': len((*self.plugMgr.group_msg_receivers,
                          *self.__group_msg_receivers_from_hand)),
            'event': len((*self.plugMgr.event_receivers,
                          *self.__event_receivers_from_hand))
        }

    @receivers.setter
    def receivers(self, _):
        self.logger.warning('The attribute receivers is read-only!')

    def __initialize_socketio(self):
        self.socketio = socketio.Client()
        self.socketio.event()(self.connect)

    def __refresh_executor(self):
        # 根据消息接收函数数量初始化线程池
        self.__executor = ThreadPoolExecutor(max_workers=min(50, len([  # 减小数量，控制消息频率
            *self.plugMgr.friend_msg_receivers,
            *self.__friend_msg_receivers_from_hand,
            *self.plugMgr.group_msg_receivers,
            *self.__group_msg_receivers_from_hand,
            *self.plugMgr.event_receivers,
            *self.__event_receivers_from_hand,
            *range(3)
        ]) * 2))

    # 手动添加
    def add_group_msg_receiver(self, func: GroupMsgReceiver):
        '''添加群消息接收函数'''
        self.__group_msg_receivers_from_hand.append(func)

    def add_friend_msg_receiver(self, func: FriendMsgReceiver):
        '''添加好友消息接收函数'''
        self.__friend_msg_receivers_from_hand.append(func)

    def add_event_receiver(self, func: EventMsgReceiver):
        '''添加事件消息接收函数'''
        self.__event_receivers_from_hand.append(func)

    ########################################################################
    # context distributor
    ########################################################################
    def __friend_context_distributor(self, context: FriendMsg):
        for f_receiver in [*self.__friend_msg_receivers_from_hand,
                           *self.plugMgr.friend_msg_receivers]:
            (self.__executor
             .submit(f_receiver, copy.deepcopy(context))
             .add_done_callback(self.__thread_pool_callback))

    def __group_context_distributor(self, context: GroupMsg):
        for g_receiver in [*self.__group_msg_receivers_from_hand,
                           *self.plugMgr.group_msg_receivers]:
            (self.__executor
             .submit(g_receiver, copy.deepcopy(context))
             .add_done_callback(self.__thread_pool_callback))

    def __event_context_distributor(self, context: EventMsg):
        for e_receiver in [*self.__event_receivers_from_hand,
                           *self.plugMgr.event_receivers]:
            (self.__executor
             .submit(e_receiver, copy.deepcopy(context))
             .add_done_callback(self.__thread_pool_callback))

    ########################################################################
    # register context middleware
    ########################################################################
    def register_friend_context_middleware(self, middleware: Callable[[FriendMsg], FriendMsg]):
        """注册好友消息中间件"""
        if self.__friend_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(friend)')
        self.__friend_context_middleware = middleware

    def register_group_context_middleware(self, middleware: Callable[[GroupMsg], GroupMsg]):
        """注册群消息中间件"""
        if self.__group_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(group)')
        self.__group_context_middleware = middleware

    def register_event_context_middleware(self, middleware: Callable[[EventMsg], EventMsg]):
        """注册事件消息中间件"""
        if self.__event_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(event)')
        self.__event_context_middleware = middleware

    ########################################################################
    # message handler
    ########################################################################
    def __thread_pool_callback(self, worker):
        worker_exception = worker.exception()
        if worker_exception:
            raise worker_exception

    def __friend_msg_handler(self, msg):
        context: FriendMsg = model_map['OnFriendMsgs'](msg)
        # 黑名单
        if context.FromUin in self.friend_blacklist:
            return
        # 中间件
        if self.__friend_context_middleware is not None:
            new_context = self.__friend_context_middleware(context)
            if isinstance(new_context, type(context)):
                context = new_context
        self.__executor.submit(self.__friend_context_distributor, context)

    def __group_msg_handler(self, msg):
        context: GroupMsg = model_map['OnGroupMsgs'](msg)
        # 黑名单
        if context.FromGroupId in self.group_blacklist:
            return
        # 中间件
        if self.__group_context_middleware is not None:
            new_context = self.__group_context_middleware(context)
            if isinstance(new_context, type(context)):
                context = new_context
        self.__executor.submit(self.__group_context_distributor, context)

    def __event_msg_handler(self, msg):
        context: EventMsg = model_map['OnEvents'](msg)
        # 中间件
        if self.__event_context_middleware is not None:
            new_context = self.__event_context_middleware(context)
            if isinstance(new_context, type(context)):
                context = new_context
        self.__executor.submit(self.__event_context_distributor, context)

    def __initialize_handlers(self):
        self.socketio.on('OnGroupMsgs')(self.__group_msg_handler)
        self.socketio.on('OnFriendMsgs')(self.__friend_msg_handler)
        self.socketio.on('OnEvents')(self.__event_msg_handler)
    ###########################################################################
    # decorators
    on_group_msg = _deco_creater('OnGroupMsgs')
    on_friend_msg = _deco_creater('OnFriendMsgs')
    on_event = _deco_creater('OnEvents')

    def __repr__(self):
        return 'IOTBOT <{}> <host-{}> <port-{}>'.format(
            " ".join([str(i) for i in self.qq]),
            self.host,
            self.port
        )
