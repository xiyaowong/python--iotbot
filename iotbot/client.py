# pylint: disable = too-many-instance-attributes
import importlib
import logging
import os
import random
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Any, Callable

import schedule
import socketio
from prettytable import PrettyTable

from .logger import Logger
from .model import FriendMsg, GroupMsg, model_map


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
    :param group_blacklist: 群黑名单, 此名单中的群聊消息不会被处理,默认为空，即全部处理
    :param friend_whitelist: 好友白名单，只有此名单中的好友消息才会被处理，默认为空，即全部处理
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
                 group_blacklist: list = None,
                 friend_whitelist: list = None,
                 log=True,
                 log_file_path=None,
                 port=8888,
                 beat_delay=60,
                 host='http://127.0.0.1'):
        self.qq = qq
        self.use_plugins = use_plugins
        self.plugin_dir = plugin_dir
        self.group_blacklist = group_blacklist or []
        self.friend_whitelist = friend_whitelist or []
        self.host = host
        self.port = port
        self.beat_delay = beat_delay
        self.logger = Logger(log_file_path)
        if not log:
            logging.disable()

        # 手动
        self.__friend_msg_receivers_from_hand = []
        self.__group_msg_receivers_from_hand = []
        self.__event_receivers_from_hand = []

        # 插件
        self.__friend_msg_receivers_from_plugin = []
        self.__group_msg_receivers_from_plugin = []
        self.__event_receivers_from_plugin = []

        # 控制频率
        self.__group_msg_dict = defaultdict(list)

        if use_plugins:
            self.refresh_plugins()

        self.__initialize_socketio()
        self.__refresh_executor()
        self.__initialize_handlers()

    def run(self):
        self.__initialize_schedulers()
        self.__run_schedule()

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
                sys.exit(0)

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
    # message(context) receivers
    ########################################################################
    def refresh_plugins(self) -> bool:
        '''刷新插件'''
        if not self.use_plugins:
            self.logger.info('未开启插件功能!')
            return False
        try:
            plugin_names = [i.split('.')[0] for i in os.listdir(self.plugin_dir)
                            if i.startswith('bot_') and i.endswith('.py')]
        except FileNotFoundError:
            self.logger.warning(f'你开启了插件功能，但是插件目录不存在[{self.plugin_dir}]')
            return False
        else:
            # 将原始清空，防止重复添加，这里用集合不能解决问题
            for i in [self.__group_msg_receivers_from_plugin,
                      self.__friend_msg_receivers_from_plugin,
                      self.__event_receivers_from_plugin]:
                i.clear()
            plugin_count = {'friend': [], 'group': [], 'event': []}  # 无关紧要的东西，用来临时保存插件信息
            for plugin_name in plugin_names:
                plugin = getattr(__import__(f'{self.plugin_dir}.{plugin_name}'), plugin_name)
                importlib.reload(plugin)
                if hasattr(plugin, 'receive_friend_msg'):
                    self.__friend_msg_receivers_from_plugin.append(plugin.receive_friend_msg)
                    plugin_count['friend'].append(plugin_name)
                if hasattr(plugin, 'receive_group_msg'):
                    self.__group_msg_receivers_from_plugin.append(plugin.receive_group_msg)
                    plugin_count['group'].append(plugin_name)
                if hasattr(plugin, 'receive_events'):
                    self.__event_receivers_from_plugin.append(plugin.receive_events)
                    plugin_count['event'].append(plugin_name)
            ################构建提示信息##################
            temp = {'friend': [], 'group': [], 'event': []}
            for category, statistic in plugin_count.items():
                for item in set(statistic):
                    temp[category].append(('{}<{}>'.format(item, statistic.count(item))))

            table = PrettyTable(['Receiver', 'Count', 'Info'])
            table.add_row([
                'Friend Msg Receiver',
                len(self.__friend_msg_receivers_from_plugin),
                ' '.join(temp['friend'])
            ])
            table.add_row([
                'Group  Msg Receiver',
                len(self.__group_msg_receivers_from_plugin),
                ' '.join(temp['group'])
            ])
            table.add_row([
                'Event      Receiver',
                len(self.__event_receivers_from_plugin),
                ' '.join(temp['event'])
            ])
            print(table)
            ###############################################
            self.__refresh_executor()
            return True

    def __refresh_executor(self):
        # 根据消息接收函数数量初始化线程池
        self.__executor = ThreadPoolExecutor(max_workers=min(50, len([  # 减小数量，控制消息频率
            *self.__friend_msg_receivers_from_plugin,
            *self.__friend_msg_receivers_from_hand,
            *self.__group_msg_receivers_from_plugin,
            *self.__group_msg_receivers_from_hand,
            *self.__event_receivers_from_plugin,
            *self.__event_receivers_from_hand,
            *range(3)
        ]) * 2))

    # 手动添加
    def add_group_msg_receiver(self, func: Callable[[GroupMsg], Any]):
        '''群消息处理'''
        self.__group_msg_receivers_from_hand.append(func)

    def add_friend_msg_receiver(self, func: Callable[[FriendMsg], Any]):
        '''好友消息'''
        self.__friend_msg_receivers_from_hand.append(func)

    def add_event_receiver(self, func: Callable[[dict], Any]):
        '''事件'''
        self.__event_receivers_from_hand.append(func)

    ########################################################################
    # context distributor
    ########################################################################
    def __friend_context_distributor(self, context: FriendMsg):
        for f_receiver in [*self.__friend_msg_receivers_from_hand, *self.__friend_msg_receivers_from_plugin]:
            self.__executor.submit(f_receiver, context).add_done_callback(self.__thread_pool_callback)

    def __group_context_distributor(self, context: GroupMsg):
        # 限制频率相关
        if context.FromUserId != context.CurrentQQ:
            if len(self.__group_msg_dict[context.FromGroupId]) > 8:
                time.sleep(random.uniform(.6, 1.2))
                # print('延时长点')
            elif len(self.__group_msg_dict[context.FromGroupId]) > 4:
                time.sleep(.3)
                # print('延时短点')
            self.__group_msg_dict[context.FromGroupId].append(0)
            # print('------------')
            # print(self.__group_msg_dict)
            # print('------------')
        ###########################################
        for g_receiver in [*self.__group_msg_receivers_from_hand, *self.__group_msg_receivers_from_plugin]:
            self.__executor.submit(g_receiver, context).add_done_callback(self.__thread_pool_callback)

    def __event_context_distributor(self, context):
        for e_receiver in [*self.__event_receivers_from_hand, *self.__event_receivers_from_plugin]:
            self.__executor.submit(e_receiver, context).add_done_callback(self.__thread_pool_callback)

    ########################################################################
    # message handler
    ########################################################################
    def __thread_pool_callback(self, worker):
        worker_exception = worker.exception()
        if worker_exception:
            raise worker_exception

    def __friend_msg_handler(self, msg):
        context = model_map['OnFriendMsgs'](msg)  # type:FriendMsg
        if self.friend_whitelist:
            if context.FromUin not in self.friend_whitelist:
                return
        self.__executor.submit(self.__friend_context_distributor, context)

    def __group_msg_handler(self, msg):
        context = model_map['OnGroupMsgs'](msg)  # type:GroupMsg
        if context.FromGroupId in self.group_blacklist:
            return
        self.__executor.submit(self.__group_context_distributor, context)

    def __event_msg_handler(self, msg):
        self.__executor.submit(self.__event_context_distributor, msg)

    def __initialize_handlers(self):
        self.socketio.on('OnGroupMsgs')(self.__group_msg_handler)
        self.socketio.on('OnFriendMsgs')(self.__friend_msg_handler)
        self.socketio.on('OnEvents')(self.__event_msg_handler)

    ########################################################################
    # 定时任务相关
    ########################################################################
    def __initialize_schedulers(self):
        schedule.every(60).seconds.do(self.__clear_msg_dict)

    def __clear_msg_dict(self):
        # print('----------clear group msg dict------------')
        # print(self.__group_msg_dict)
        self.__group_msg_dict.clear()

    def __run_schedule_do_not_call(self):
        while True:
            schedule.run_pending()

    def __run_schedule(self):
        schedule_thread = Thread(target=self.__run_schedule_do_not_call)
        schedule_thread.start()
        ########################################################################

    on_group_msg = _deco_creater('OnGroupMsgs')
    on_friend_msg = _deco_creater('OnFriendMsgs')
    on_event = _deco_creater('OnEvents')

    def __repr__(self):
        return f'IOTBOT <{self.qq}>'
