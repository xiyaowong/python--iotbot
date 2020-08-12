"""一些常用的方法

Tips: 如果开启队列，请将`action`定义为全局变量!,最重要的一点，开启队列方法都没有返回值，
    所以对于获取信息的api，千万不能用这个模式

对于发送语音，图片的方法，建议将timeout设置很短，因为暂时发现这类请求因为需要文件上传操作，
响应时间会较长，而且目前来看，如果文件较大导致上传时间太长，IOTBOT端会报错, IOTBOT响应的结果一定是错误的,
不过发送去的操作是能正常完成的。
"""
import functools
import re
import sys
import time
import traceback
from queue import Queue
from queue import deque
from threading import Thread
from typing import Any
from typing import Callable
from typing import Union

import requests
from loguru import logger
from requests.exceptions import Timeout

from .client import IOTBOT
from .config import config

try:
    import ujson as json
except Exception:
    import json

logger.remove()
logger.add(
    sys.stdout,
    format='{level.icon} {time:YYYY-MM-DD HH:mm:ss} <lvl>{level}\t{message}</lvl>',
    colorize=True
)

WAIT_THEN_RUN = 1  # 延时一段时间，然后继续发送
STOP_AND_DISCARD = 2  # 停止发送，删除剩余任务


class Action:
    '''
    :param qq_or_bot: qq号或者机器人实例(`IOTBOT`)
    :param queue: 是否开启队列，开启后任务将按顺序发送并延时指定时间，此参数与`queue_delay`对应
                  启用后，发送方法`没有返回值`
    :param queue_delay: 与`队列`对应, 开启队列时发送每条消息间的延时, 保持默认即可
    :param send_per_minute: 与`队列`对应, 指定每分钟最多执行多少条任务
    :param send_per_minute_behavior: 与参数`send_per_minute`相关联, 指定每分钟发送量达到
                                    限定值后，对剩余发送任务的处理方式
    :param send_per_minute_callback: 当达到每分钟限制后调用的函数，接收参数为一个`元组`(剩余时间, 剩余任务数)
    :param timeout: 等待IOTBOT响应时间和发送请求的延时
    :param api_path: 方法路径
    :param port: 端口
    :param host: ip
    '''

    def __init__(self,
                 qq_or_bot: Union[int, IOTBOT] = None,
                 queue: bool = False,
                 queue_delay: Union[int, float] = 1.1,
                 send_per_minute: int = None,
                 send_per_minute_behavior: int = WAIT_THEN_RUN,
                 send_per_minute_callback: Callable[[int, int], Any] = None,
                 timeout: int = 15,
                 api_path: str = '/v1/LuaApiCaller',
                 port: int = 8888,
                 host: str = 'http://127.0.0.1'):
        self.__timeout = timeout
        self.__api_path = api_path
        self.__port = config.port or port
        self.__host = config.host or host
        if isinstance(qq_or_bot, IOTBOT):
            self.bind_bot(qq_or_bot)
        else:
            self.qq = int(qq_or_bot)

        # 初始化用来控制每分钟的发送频率的相关配置
        if queue and send_per_minute is not None:
            assert isinstance(send_per_minute, int), '`send_per_minute` must be `integer`'
            assert 0 < send_per_minute < 40, '0 到 40 之间！'  # emm
            assert send_per_minute_behavior in (WAIT_THEN_RUN, STOP_AND_DISCARD), '二选一'
            self.__limit_send = True
            self.__send_count_deque = deque(maxlen=send_per_minute)
            self.__send_per_minute_behavior = send_per_minute_behavior
            self.__send_per_minute_callback = send_per_minute_callback
        else:
            self.__limit_send = False  # 发送线程需要这个数，要放在队列相关前面

        # 任务队列相关
        if queue:
            self.__use_queue = True
            self.__queue_delay = queue_delay
            self.__send_queue = Queue(maxsize=1000)
            self.__last_send_time = time.time()
            self._start_send_thread()
        else:
            self.__use_queue = False

    def _start_send_thread(self):
        # 如果模块有额外的线程，reload之后，之前的线程还是会运行.
        # 虽然不影响程序使用，但应该挺浪费资源
        # 目前找不到解决方法，暂时先用一个标记存储发送线程的状态，通过设置队列超时来跳出线程
        # 添加队列任务时进行判断，如果线程已死就重启
        self.__is_send_thread_dead = False
        # 开启发送队列线程
        Thread(target=self.__send_thread).start()

    def __send_thread(self):
        """
        发送队列线程
        负责执行队列的任务，并判断是否应该立即执行
        包括处理每分钟发送数量限制
        """
        while True:
            # 见 _start_send_thread 注释
            try:
                # 3h
                job = self.__send_queue.get(timeout=3 * 60 * 60)  # type: Callable
            except Exception:
                self.__is_send_thread_dead = True
                break
            left_time = self.__queue_delay - (time.time() - self.__last_send_time)
            if left_time > 0:
                # print(f'还没到发送时间...,请等待{left_time}s')
                time.sleep(left_time)  # 发送间隔延时

            try:
                # print('即将发送....')
                job()
                if self.__limit_send:  # 发送限额
                    self.__send_count_deque.append(time.time())
                    # print(self.__send_count_deque)
                    if len(self.__send_count_deque) == self.__send_count_deque.maxlen:
                        should_limited_time = 60 - (self.__send_count_deque[-1] - self.__send_count_deque[0])
                        # print('should_limited_time -> ', should_limited_time)
                        if should_limited_time > 0:
                            # print('每分钟发送数量已达上限...')
                            if self.__send_per_minute_behavior == STOP_AND_DISCARD:
                                # print('清空队列...')
                                while not self.__send_queue.empty():  # 貌似没有清空方法
                                    self.__send_queue.get()
                            if self.__send_per_minute_callback is not None:
                                self.__send_per_minute_callback((should_limited_time, self.__send_queue.qsize()))
                            time.sleep(should_limited_time)
                            self.__send_count_deque.clear()
                            # if self.__send_per_minute_behavior == WAIT_THEN_RUN:
                            #     print('延时然后继续运行...')
                            #     time.sleep(should_limited_time)
            except Exception:
                logger.exception('发送线程内任务出错')
            finally:
                self.__last_send_time = time.time()
                # print(f'上次运行时间：{self.__last_send_time}')

    def bind_bot(self, bot: IOTBOT):
        """绑定机器人"""
        self.qq = bot.qq[0]
        self.__port = bot.port
        self.__host = bot.host

    def send_friend_text_msg(self, toUser: int, content: str, timeout=5, **kwargs) -> dict:
        """发送好友文本消息"""
        data = {
            "toUser": toUser,
            "sendToType": 1,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": 0,
            "atUser": 0,
            "replayInfo": None
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def get_user_list(self, timeout=5, **kwargs) -> dict:
        """获取好友列表"""
        return self.baseSender('post', 'GetQQUserList', {"StartIndex": 0}, timeout=timeout, **kwargs)

    def send_friend_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf='', timeout=5, **kwargs) -> dict:
        """发送好友语音消息"""
        data = {
            "toUser": toUser,
            "sendToType": 1,
            "sendMsgType": "VoiceMsg",
            "content": "",
            "groupid": 0,
            "atUser": 0,
            "voiceUrl": voiceUrl,
            "voiceBase64Buf": voiceBase64Buf
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_friend_pic_msg(self, toUser, content='', picUrl='', picBase64Buf='', fileMd5='',
                            flashPic=False, timeout=5, **kwargs) -> dict:
        """发送好友图片消息"""
        data = {
            "toUser": toUser,
            "sendToType": 1,
            "sendMsgType": "PicMsg",
            "content": content,
            "groupid": 0,
            "atUser": 0,
            "picUrl": picUrl,
            "picBase64Buf": picBase64Buf,
            "fileMd5": fileMd5,
            "flashPic": flashPic
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_group_text_msg(self, toUser: int, content='', atUser=0, timeout=5, **kwargs) -> dict:
        """发送群文字消息"""
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_group_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf='', timeout=5, **kwargs) -> dict:
        """发送群语音"""
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "VoiceMsg",
            "content": '',
            "groupid": 0,
            "atUser": 0,
            "voiceUrl": voiceUrl,
            "voiceBase64Buf": voiceBase64Buf
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_group_pic_msg(self, toUser: int, picUrl='', flashPic=False, atUser=0, content='',
                           picBase64Buf='', fileMd5='', timeout=5, **kwargs) -> dict:
        """发送群图片
        Tips:
            [秀图id] 各id对应效果
            40000   秀图
            40001   幻影
            40002   抖动
            40003   生日
            40004   爱你
            40005   征友
            40006   无(只显示大图无特效)

            [PICFLAG] 改变图文消息顺序
        """
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "PicMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser,
            "picUrl": picUrl,
            "picBase64Buf": picBase64Buf,
            "fileMd5": fileMd5,
            "flashPic": flashPic
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_private_text_msg(self, toUser: int, content: str, groupid: int, timeout=5, **kwargs) -> dict:
        """发送私聊文字消息"""
        data = {
            "toUser": toUser,
            "sendToType": 3,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": groupid,
            "atUser": 0
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_private_voice_msg(self, toUser: int, groupid, voiceUrl='', voiceBase64Buf='', timeout=5, **kwargs) -> dict:
        """发送私聊语音"""
        data = {
            "toUser": toUser,
            "sendToType": 3,
            "sendMsgType": "VoiceMsg",
            "content": "",
            "groupid": groupid,
            "atUser": 0,
            "voiceUrl": voiceUrl,
            "voiceBase64Buf": voiceBase64Buf
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_private_pic_msg(self, toUser, groupid, picUrl='', picBase64Buf='', content='',
                             fileMd5='', timeout=10, **kwargs) -> dict:
        """发送私聊图片"""
        data = {
            "toUser": toUser,
            "sendToType": 3,
            "sendMsgType": "PicMsg",
            "content": content,
            "groupid": groupid,
            "atUser": 0,
            "picUrl": picUrl,
            "picBase64Buf": picBase64Buf,
            "fileMd5": fileMd5
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_group_json_msg(self, toUser: int, content='', atUser=0, timeout=5, **kwargs) -> dict:
        """发送群Json类型信息
        :param content: 可以为json文本，或者字典类型
        """
        if isinstance(content, dict):
            content = json.dumps(content)
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "JsonMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def send_group_xml_msg(self, toUser: int, content='', atUser=0, timeout=5, **kwargs) -> dict:
        """发送群Xml类型信息"""
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "XmlMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def revoke_msg(self, groupid: int, msgseq: int, msgrandom: int, type_=1, timeout=5, **kwargs) -> dict:
        """撤回消息
        :param type_: 1: RevokeMsg | 2: PbMessageSvc.PbMsgWithDraw
        """
        funcname = 'RevokeMsg' if type_ == 1 else 'PbMessageSvc.PbMsgWithDraw'
        data = {"GroupID": groupid, "MsgSeq": msgseq, "MsgRandom": msgrandom}
        return self.baseSender('POST', funcname, data, timeout, **kwargs)

    def search_group(self, content, page=0, timeout=5, **kwargs) -> dict:
        """搜索群组"""
        return self.baseSender('POST', 'SearchGroup', {"Content": content, "Page": page}, timeout, **kwargs)

    def get_user_info(self, userID: int, timeout=5, **kwargs) -> dict:
        '''获取用户信息'''
        return self.baseSender('POST', 'GetUserInfo', {'UserID': userID, 'GroupID': 0}, timeout, **kwargs)

    def get_cookies(self, timeout=2, **kwargs) -> dict:
        """获取cookies"""
        return self.baseSender('GET', 'GetUserCook', timeout=timeout, **kwargs)

    def get_group_list(self, timeout=5, **kwargs) -> dict:
        """获取群组列表"""
        return self.baseSender('POST', 'GetGroupList', {"NextToken": ""}, timeout, **kwargs)

    def get_group_admin_list(self, groupid: int, timeout=5, **kwargs) -> dict:
        """获取群管理员列表"""
        data = self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": 0}, timeout, **kwargs)
        LastUin = data['LastUin']
        MemberList = data['MemberList']
        AdminList = []
        while LastUin != 0:
            time.sleep(1.1)
            data = self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": LastUin}, timeout, **kwargs)
            LastUin = data['LastUin']
            MemberList += data['MemberList']
            AdminList = [i for i in MemberList if i['GroupAdmin'] != 0]
            if len(AdminList) == 10:
                break
        del LastUin, MemberList
        return AdminList

    def get_group_admin_list(self, groupid: int, timeout=5, **kwargs) -> dict:
        """获取群管理员列表"""
        AdminList = []
        data = self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": 0}, timeout, **kwargs)
        while True:
            LastUin = data['LastUin']
            MemberList = data['MemberList']
            for Admin in MemberList:
                if Admin['GroupAdmin'] == 1:
                    AdminList.append(Admin)
            if LastUin == 0:
                break
            time.sleep(1.1)
            data = self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": LastUin}, timeout,
                                   **kwargs)
        return AdminList

    def set_unique_title(self, groupid: int, userid: int, Title: str, timeout=1, **kwargs) -> dict:
        """设置群成员头衔"""
        return self.baseSender('POST', 'OidbSvc.0x8fc_2', {"GroupID": groupid, "UserID": userid, "NewTitle": Title}, timeout, **kwargs)

    def modify_group_card(self, userID: int, groupID: int, newNick: str, timeout=5, **kwargs) -> dict:
        '''修改群名片

        :params userID: 修改的QQ号
        :params groupID: 群号
        :params newNick: 新群名片

        '''
        data = {
            'UserID': userID,
            'GroupID': groupID,
            'NewNick': newNick
        }
        return self.baseSender('POST', 'ModifyGroupCard', data, timeout, **kwargs)

    def refresh_keys(self, timeout=20) -> bool:
        '''刷新key二次登陆, 成功返回True， 失败返回False'''
        try:
            rep = requests.get(f'{self.__host}:{self.__port}/v1/RefreshKeys?qq={self.qq}', timeout=timeout)
            if rep.json()['Ret'] == 'ok':
                return True
        except Exception:
            pass
        return False

    def add_friend(self, userID: int, groupID: int, content='加个好友!', AddFromSource=2004, timeout=20, **kwargs) -> dict:
        """添加好友"""
        data = {
            "AddUserUid": userID,
            "FromGroupID": groupID,
            "AddFromSource": AddFromSource,
            "Content": content
        }
        return self.baseSender('POST', 'AddQQUser', data, timeout, **kwargs)

    def get_friend_file(self, FileID: str, timeout=20, **kwargs) -> dict:
        """获取好友文件下载链接"""
        funcname = 'OfflineFilleHandleSvr.pb_ftn_CMD_REQ_APPLY_DOWNLOAD-1200'
        data = {
            'FileID': FileID
        }
        return self.baseSender('POST', funcname, data, timeout, **kwargs)

    def get_group_file(self, groupID: int, FileID: str, timeout=20, **kwargs) -> dict:
        """获取群文件下载链接"""
        funcname = 'OidbSvc.0x6d6_2'
        data = {
            'FileID': FileID,
            'GroupID': groupID
        }
        return self.baseSender('POST', funcname, data, timeout, **kwargs)

    def set_group_announce(self, groupID: int, Title: str, Text: str, Pinned=0, Type=10, timeout=5, **kwargs) -> dict:
        """设置群公告"""
        data = {
            'GroupID': groupID,  # 发布的群号
            "Title": Title,  # 公告标题
            "Text": Text,  # 公告内容
            "Pinned": Pinned,  # 1为置顶,0为普通公告
            "Type": Type  # 发布类型(10为使用弹窗公告,20为发送给新成员,其他暂未知)
        }
        try:
            res = requests.post(f'{self.__host}:{self.__port}/v1/Group/Announce?qq={self.qq}', data=data, timeout=timeout, **kwargs)
            return res.json()
        except Exception:
            return {}

    def deal_friend(self) -> dict:
        """处理好友请求"""
        pass

    def all_shut_up_on(self, groupid, timeout=20, **kwargs) -> dict:
        """开启全员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x89a_0', {"GroupID": groupid, "Switch": 1}, timeout, **kwargs)

    def all_shut_up_off(self, groupid, timeout=20, **kwargs) -> dict:
        """关闭全员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x89a_0', {"GroupID": groupid, "Switch": 0}, timeout, **kwargs)

    def you_shut_up(self, groupid, userid, shut_time=0, timeout=20, **kwargs) -> dict:
        """群成员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x570_8', {"GroupID": groupid, "ShutUpUserID": userid, "ShutTime": shut_time}, timeout, **kwargs)

    def like(self, userid: int, timeout=10, **kwargs) -> dict:
        """通用点赞"""
        return self.baseSender('POST', 'OidbSvc.0x7e5_4', {"UserID": userid}, timeout, **kwargs)

    def like_2(self, userid: int, timeout=10, **kwargs) -> dict:
        """测试赞(这里的测试只是与webapi描述一致)"""
        return self.baseSender('POST', 'QQZan', {"UserID": userid}, timeout, **kwargs)

    def logout(self, flag=False, timeout=5, **kwargs) -> bool:
        '''退出QQ
        :param flag:是否删除设备信息文件
        '''
        return self.baseSender('POST', 'LogOut', {"Flag": flag}, timeout, **kwargs)

    def get_login_qrcode(self) -> str:
        '''返回登录二维码的base64'''
        try:
            resp = requests.get(
                '{}:{}/v1/Login/GetQRcode'.format(self.__host, self.__port), timeout=10)
        except Exception as e:
            logger.error('http请求错误 %s' % str(e))
        else:
            try:
                return re.findall(r'"data:image/png;base64,(.*?)"', resp.text)[0]
            except IndexError:
                logger.error('base64获取失败')
        return ''

    def baseSender(self,
                   method: str,
                   funcname: str,
                   data: dict = None,
                   timeout: int = None,
                   api_path: str = None,
                   iot_timeout: int = None,
                   bot_qq: int = None) -> Union[dict, bool]:
        """
        :param method: 请求方法
        :param funcname: 请求类型
        :param data: post的数据
        :param timeout: 发送请求等待响应的时间
        :param api_path: 默认为/v1/LuaApiCaller
        :param iot_timeout: IOT端处理请求等待的时间
        :param bot_qq: 机器人QQ

        :return: iotbot端返回的json数据(字典)，如果返回内容非json则返回空字典
        """
        job = functools.partial(
            self._baseSender,
            method=method,
            funcname=funcname,
            data=data,
            timeout=timeout,
            api_path=api_path,
            iot_timeout=iot_timeout,
            bot_qq=bot_qq
        )
        functools.update_wrapper(job, self.baseSender)
        if self.__use_queue:
            self.__send_queue.put(job)
            ###########################################
            if self.__is_send_thread_dead:  # 重启线程
                self._start_send_thread()
            ###########################################
            # print('加入队列...')
            return None
        # print('不加入队列...')
        return job()

    def _baseSender(self,
                    method: str,
                    funcname: str,
                    data: dict = None,
                    timeout: int = None,
                    api_path: str = None,
                    iot_timeout: int = None,
                    bot_qq: int = None) -> Union[dict, bool]:
        params = {
            'funcname': funcname,
            'timeout': iot_timeout or self.__timeout,
            'qq': bot_qq or self.qq
        }
        if data is None:
            data = {}
        try:
            rep = requests.request(
                method=method,
                url='{}:{}{}'.format(self.__host, self.__port, api_path or self.__api_path),
                headers={'Content-Type': 'application/json'},
                params=params,
                json=data,
                timeout=timeout or self.__timeout
            )
            response = {}
            if rep.status_code == 200:
                response = rep.json()
                if response is None:  # 什么时候这个东西会是None? 0.o
                    return {}
                if 'Ret' in response:
                    if response['Ret'] != 0:
                        if response['Ret'] == 241:
                            logger.error(f'请求频繁: {response}')
                        else:
                            logger.error(f'请求发送成功, 但处理失败: {response}')
            else:
                logger.error(f'*****不是预期的Http响应码: {rep.status_code}*****')
            return response
        except Exception as e:
            if isinstance(e, Timeout):
                logger.warning('响应超时，但不代表处理未成功, 结果未知!')
            else:
                logger.error(f'出现错误: {traceback.format_exc()}')
            return {}
