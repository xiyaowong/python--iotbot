# pylint: disable = too-many-instance-attributes
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import socketio

from .logger import Logger
from .model import model_map


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
    :param qq: 机器人QQ号
    :param use_plugins: 是否开启插件功能
    :param plugin_dir: 插件存放目录
    :param log: 是否开启log
    :param log_file_path: 日志文件路径
    :param port: 运行端口
    :param beat_delay: 心跳延时时间（s）
    :param host: ip，需要包含协议
    """

    def __init__(self,
                 qq: int,
                 use_plugins=False,
                 plugin_dir='plugins',
                 log=True,
                 log_file_path=None,
                 port=8888,
                 beat_delay=60,
                 host='http://127.0.0.1'):
        self.qq = qq
        self.use_plugins = use_plugins
        self.plugin_dir = plugin_dir
        self.host = host
        self.port = port
        self.beat_delay = beat_delay
        self.logger = Logger(log_file_path)
        if not log:
            logging.disable()

        self.__friend_msg_receivers_from_hand = []
        self.__group_msg_receivers_from_hand = []
        self.__event_receivers_from_hand = []

        self.__friend_msg_receivers_from_plugin = []
        self.__group_msg_receivers_from_plugin = []
        self.__event_receivers_from_plugin = []

        if use_plugins:
            self.refresh_plugins()

        self.__initialize_socketio()
        self.__refresh_executor()
        self.__initialize_handlers()

    def run(self):
        try:
            self.logger.info('Connecting to the server...')
            self.socketio.connect(f'{self.host}:{self.port}', transports=['websocket'])
            self.socketio.wait()
        except Exception as e:
            self.logger.error(f'启动失败 -> {e}')
            sys.exit(1)

    def connect(self):
        self.logger.info('Connected to server successfully!')
        while True:
            self.socketio.emit('GetWebConn', str(self.qq))
            time.sleep(self.beat_delay)

    @property
    def receivers(self):
        '''消息处理函数数量'''
        return {
            'friend': len((*self.__friend_msg_receivers_from_plugin,
                           *self.__friend_msg_receivers_from_hand)),
            'group': len((*self.__group_msg_receivers_from_plugin,
                          *self.__group_msg_receivers_from_hand)),
            'event': len((*self.__event_receivers_from_plugin,
                          *self.__event_receivers_from_hand))
        }

    @receivers.setter
    def receivers(self, _):
        self.logger.warning('The attribute receivers is read-only!')

    def __initialize_socketio(self):
        self.socketio = socketio.Client()
        self.socketio.event()(self.connect)

    ########################################################################
    # 处理信息接收函数
    ########################################################################
    def refresh_plugins(self):
        '''刷新插件'''
        if not self.use_plugins:
            self.logger.info('未开启插件功能!')
            return
        try:
            plugin_names = [i.split('.')[0] for i in os.listdir(self.plugin_dir) if i.startswith('bot_')]
            # 将原始清空，防止重复添加，这里用集合不能解决问题
            for i in [self.__group_msg_receivers_from_plugin,
                      self.__friend_msg_receivers_from_plugin,
                      self.__event_receivers_from_plugin]:
                i.clear()
            print('Loading plugins...')
            for plugin_name in plugin_names:
                temp = __import__(f'{self.plugin_dir}.{plugin_name}')  # pylint: disable=unused-variable
                plugin = eval(f'temp.{plugin_name}')  # pylint: disable=eval-used
                if hasattr(plugin, 'receive_friend_msg'):
                    self.__friend_msg_receivers_from_plugin.append(plugin.receive_friend_msg)
                if hasattr(plugin, 'receive_group_msg'):
                    self.__group_msg_receivers_from_plugin.append(plugin.receive_group_msg)
                if hasattr(plugin, 'receive_events'):
                    self.__event_receivers_from_plugin.append(plugin.receive_events)
            print(f'[Friend Msg Receivers] \t{len(self.__friend_msg_receivers_from_plugin)}')
            print(f'[Group Msg Receivers] \t{len(self.__group_msg_receivers_from_plugin)}')
            print(f'[Event Receivers] \t{len(self.__event_receivers_from_plugin)}')
            print('Load plugins completely!')
            self.__refresh_executor()
        except FileNotFoundError:
            self.logger.warning(f'你开启了插件功能，但是插件目录不存在[{self.plugin_dir}]')

    def __refresh_executor(self):
        # 根据函数处理数量初始化线程池
        self.__executor = ThreadPoolExecutor(max_workers=min(200, len([
            *self.__friend_msg_receivers_from_plugin,
            *self.__friend_msg_receivers_from_hand,
            *self.__group_msg_receivers_from_plugin,
            *self.__group_msg_receivers_from_hand,
            *self.__event_receivers_from_plugin,
            *self.__event_receivers_from_hand,
            *range(10)
        ]) * 3))  # 添加10*3个占位

    # 手动添加
    def add_group_msg_receiver(self, func: Callable):
        '''群消息处理'''
        self.__group_msg_receivers_from_hand.append(func)

    def add_friend_msg_receiver(self, func: Callable):
        '''好友消息'''
        self.__friend_msg_receivers_from_hand.append(func)

    def add_event_receiver(self, func: Callable):
        '''事件'''
        self.__event_receivers_from_hand.append(func)

    ########################################################################
    # message handler
    ########################################################################
    def __thread_pool_callback(self, worker):
        worker_exception = worker.exception()
        if worker_exception:
            raise worker_exception

    def __friend_msg_handler(self, context):
        for f_receiver in [*self.__friend_msg_receivers_from_hand, *self.__friend_msg_receivers_from_plugin]:
            self.__executor.submit(f_receiver,
                                   model_map['OnFriendMsgs'](context)).add_done_callback(self.__thread_pool_callback)

    def __group_msg_handler(self, context):
        for g_receiver in [*self.__group_msg_receivers_from_hand, *self.__group_msg_receivers_from_plugin]:
            self.__executor.submit(g_receiver,
                                   model_map['OnGroupMsgs'](context)).add_done_callback(self.__thread_pool_callback)

    def __event_handler(self, context):
        for e_receiver in [*self.__event_receivers_from_hand, *self.__event_receivers_from_plugin]:
            self.__executor.submit(e_receiver,
                                   context).add_done_callback(self.__thread_pool_callback)

    def __initialize_handlers(self):
        self.socketio.on('OnGroupMsgs')(self.__group_msg_handler)
        self.socketio.on('OnFriendMsgs')(self.__friend_msg_handler)
        self.socketio.on('OnEvents')(self.__event_handler)
    ########################################################################

    on_group_msg = _deco_creater('OnGroupMsgs')
    on_friend_msg = _deco_creater('OnFriendMsgs')
    on_event = _deco_creater('OnEvents')
