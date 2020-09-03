import copy
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Union

import socketio
from schedule import Scheduler as _Scheduler

from .config import config
from .logger import logger
from .model import EventMsg, FriendMsg, GroupMsg, model_map
from .plugin import PluginManager
from .typing import EventMsgReceiver, FriendMsgReceiver, GroupMsgReceiver


def _deco_creater(bind_type):
    def deco(self, func):
        if bind_type == 'OnGroupMsgs':
            self.add_group_msg_receiver(func)
        elif bind_type == 'OnFriendMsgs':
            self.add_friend_msg_receiver(func)
        else:
            self.add_event_receiver(func)

    return deco


class IOTBOT:  # pylint: disable = too-many-instance-attributes
    """
    :param qq: 机器人QQ号(多Q就传qq号列表)
    :param use_plugins: 是否开启插件功能
    :param plugin_dir: 插件存放目录
    :param group_blacklist: 群黑名单, 此名单中的群聊消息不会被处理,默认为空，即全部处理
    :param friend_whitelist: 好友白名单，只有此名单中的好友消息才会被处理，默认为空，即全部处理
    :param log: 是否开启日志
    :param log_file: 是否文件日志
    :param port: 运行端口
    :param beat_delay: 心跳延时时间（s）
    :param host: ip，需要包含schema
    """

    def __init__(
        self,
        qq: Union[int, List[int]],
        use_plugins: bool = False,
        plugin_dir: str = 'plugins',
        group_blacklist: List[int] = None,
        friend_blacklist: List[int] = None,
        log: bool = True,
        log_file: bool = True,
        port: int = 8888,
        host: str = 'http://127.0.0.1',
    ):
        if isinstance(qq, Sequence):
            self.qq = list(qq)
        else:
            self.qq = [qq]
        self.use_plugins = use_plugins
        self.plugin_dir = plugin_dir
        self.host = config.host or host
        self.port = config.port or port
        self.group_blacklist = set(config.group_blacklist or group_blacklist or [])
        self.friend_blacklist = set(config.friend_blacklist or friend_blacklist or [])

        # 作为程序是否应该退出的标志，以便后续用到，如定时任务
        self._exit = False

        if log:
            if log_file:
                logger.add(
                    './logs/{time}.log',
                    format='{time:YYYY-MM-DD HH:mm} {level}\t{message}',
                    rotation='1 day',
                    encoding='utf-8',
                )
        else:
            logger.disable(__name__)

        # 用于定时任务
        self.scheduler = _Scheduler()

        # 手动添加的消息接收函数
        self.__friend_msg_receivers_from_hand = []
        self.__group_msg_receivers_from_hand = []
        self.__event_receivers_from_hand = []

        # webhook 里的消息接收函数，是特例
        if config.webhook:
            from . import webhook  # pylint:disable=import-outside-toplevel

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
            print(self.plugin_status)

        # 依次各种初始化
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

    def remove_plugin(self, plugin_name: str):
        '''停用指定插件'''
        self.plugMgr.remove_plugin(plugin_name)

    def recover_plugin(self, plugin_name: str):
        '''启用指定插件'''
        self.plugMgr.recover_plugin(plugin_name)

    @property
    def plugin_status(self):
        '''插件启用状态'''
        return self.plugMgr.info_table

    @property
    def plugins(self):
        '''插件名列表'''
        return self.plugMgr.plugins

    @property
    def removed_plugins(self):
        '''已停用的插件名列表'''
        return self.plugMgr.removed_plugins

    ########################################################################

    # 调度定时任务
    def _run_padding(self):
        logger.info(f'{len(self.scheduler.jobs)} tasks that are scheduled to run.')
        while True:
            # 定时任务不是主角，所以必须其他工作正常才运行
            if self._exit:
                return
            s = self.scheduler
            runnable_jobs = (job for job in s.jobs if job.should_run)
            for job in sorted(runnable_jobs):
                if hasattr(job.job_func, '__name__'):
                    job_func_name = job.job_func.__name__
                else:
                    job_func_name = repr(job.job_func)
                logger.info('Running task => %s' % job_func_name)
                s._run_job(job)  # pylint: disable=protected-access
            # 避免不必要的循环
            # 因为定时任务间隔都很长，进入延时后并不能很好的判断self._exit来退出
            # 所以这里每次只延时`delay`秒就判断一次是否应该退出
            delay = 5
            t = int(s.idle_seconds - 5)  # 延时不是必要的，减去5s抵消下面的时间消耗
            if t <= 0:
                continue
            for _ in range(t // delay):
                if self._exit:
                    return
                time.sleep(delay)

    def run(self):
        logger.info('Connecting to the server...')
        try:
            self.socketio.connect(f'{self.host}:{self.port}', transports=['websocket'])
        except Exception:
            logger.exception('连接失败')
            self.__executor.shutdown(False)
            self._exit = True
            sys.exit(1)
        else:
            try:
                self.socketio.wait()
            except KeyboardInterrupt:
                self.__executor.shutdown(wait=False)
                self._exit = True
                print('\nbye~')
                sys.exit(0)

    def connect(self):
        logger.success('Connected to server successfully!')

        # GetWebConn
        for qq in self.qq:
            self.socketio.emit(
                'GetWebConn',
                str(qq),
                callback=lambda x: logger.info(
                    f'GetWebConn -> {qq} => {x}'  # pylint: disable=cell-var-from-loop
                ),
            )

        # 启动定时任务
        if len(self.scheduler.jobs) != 0:
            self.__executor.submit(self._run_padding).add_done_callback(
                self.__thread_pool_callback
            )

    @property
    def receivers(self):
        '''消息处理函数数量'''
        return {
            'friend': len(
                (
                    *self.plugMgr.friend_msg_receivers,
                    *self.__friend_msg_receivers_from_hand,
                )
            ),
            'group': len(
                (
                    *self.plugMgr.group_msg_receivers,
                    *self.__group_msg_receivers_from_hand,
                )
            ),
            'event': len(
                (*self.plugMgr.event_receivers, *self.__event_receivers_from_hand)
            ),
        }

    @receivers.setter
    def receivers(self, _):
        logger.warning('The attribute receivers is read-only!')

    def __initialize_socketio(self):
        self.socketio = socketio.Client()
        self.socketio.event()(self.connect)

    def __refresh_executor(self):
        # 根据消息接收函数数量初始化线程池
        self.__executor = ThreadPoolExecutor(
            max_workers=min(
                50,
                len(
                    [  # 减小数量，控制消息频率
                        *self.plugMgr.friend_msg_receivers,
                        *self.__friend_msg_receivers_from_hand,
                        *self.plugMgr.group_msg_receivers,
                        *self.__group_msg_receivers_from_hand,
                        *self.plugMgr.event_receivers,
                        *self.__event_receivers_from_hand,
                        *range(3),
                    ]
                )
                * 2,
            )
        )

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
        for f_receiver in [
            *self.__friend_msg_receivers_from_hand,
            *self.plugMgr.friend_msg_receivers,
        ]:
            self.__executor.submit(
                f_receiver, copy.deepcopy(context)
            ).add_done_callback(self.__thread_pool_callback)

    def __group_context_distributor(self, context: GroupMsg):
        for g_receiver in [
            *self.__group_msg_receivers_from_hand,
            *self.plugMgr.group_msg_receivers,
        ]:
            self.__executor.submit(
                g_receiver, copy.deepcopy(context)
            ).add_done_callback(self.__thread_pool_callback)

    def __event_context_distributor(self, context: EventMsg):
        for e_receiver in [
            *self.__event_receivers_from_hand,
            *self.plugMgr.event_receivers,
        ]:
            self.__executor.submit(
                e_receiver, copy.deepcopy(context)
            ).add_done_callback(self.__thread_pool_callback)

    ########################################################################
    # register context middleware
    ########################################################################
    def register_friend_context_middleware(
        self, middleware: Callable[[FriendMsg], FriendMsg]
    ):
        """注册好友消息中间件"""
        if self.__friend_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(friend)')
        self.__friend_context_middleware = middleware

    def register_group_context_middleware(
        self, middleware: Callable[[GroupMsg], GroupMsg]
    ):
        """注册群消息中间件"""
        if self.__group_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(group)')
        self.__group_context_middleware = middleware

    def register_event_context_middleware(
        self, middleware: Callable[[EventMsg], EventMsg]
    ):
        """注册事件消息中间件"""
        if self.__event_context_middleware is not None:
            raise Exception('Cannot register more than one middleware(event)')
        self.__event_context_middleware = middleware

    ########################################################################
    # message handler
    ########################################################################
    @logger.catch
    def __thread_pool_callback(self, worker):
        worker_exception = worker.exception()
        if worker_exception:
            raise worker_exception

    def __friend_msg_handler(self, msg):
        context: FriendMsg = model_map['OnFriendMsgs'](msg)
        logger.info(f'{context.__class__.__name__} ->  {context.data}')
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
        logger.info(f'{context.__class__.__name__} ->  {context.data}')
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
        logger.info(f'{context.__class__.__name__} ->  {context.data}')
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
            " ".join([str(i) for i in self.qq]), self.host, self.port
        )
