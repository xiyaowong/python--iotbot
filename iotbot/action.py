"""一些常用的方法

Tips: 如果开启队列，请将`action`定义为全局变量!,最重要的一点，开启队列方法都没有返回值，
    所以对于获取信息的api，千万不能用这个模式

对于发送语音，图片的方法，建议将timeout设置很短，因为暂时发现这类请求因为需要文件上传操作，
响应时间会较长，而且目前来看，如果文件较大导致上传时间太长，IOTBOT端会报错, IOTBOT响应的结果一定是错误的,
不过发送去的操作是能正常完成的。
"""
import functools
import queue
import re
import threading
import time
import traceback
from typing import Callable
from typing import Generator
from typing import List
from typing import Union

import requests
from requests.exceptions import Timeout

from .client import IOTBOT
from .config import config
from .logger import logger

try:
    import ujson as json
except Exception:
    import json


class _Task:
    def __init__(self,
                 target: Callable,
                 args: tuple = None,
                 callback: Callable = None):
        args = args or tuple()
        self.target = functools.partial(target, *args)
        functools.update_wrapper(self.target, target)
        self.callback = callback


class _SendThread(threading.Thread):
    def __init__(self, delay=1.1):
        super().__init__()
        self.tasks = queue.Queue(maxsize=-1)
        self.running = False
        self.delay = delay
        self.last_send_time = time.time()

    def run(self):
        self.running = True
        while True:
            try:
                # 因为重载(importlib.relaod)之后，线程仍会在后台运行
                # 暂时使用超时跳出线程
                # 线程停了之后，被重载后，是不是会被gc??? 0.o
                task: _Task = self.tasks.get(timeout=30 * 60)  # 30min
            except queue.Empty:
                self.running = False
                break
            else:
                should_wait = self.delay - (time.time() - self.last_send_time)
                if should_wait > 0:
                    time.sleep(should_wait)
                try:
                    ret = task.target()
                    if task.callback is not None:
                        task.callback(ret)
                except Exception:
                    logger.exception('Action发送线程出错')
                finally:
                    self.last_send_time = time.time()

    def start(self):
        # 强改内部方法以允许重复执行start方法, 暂时不知道这样做有什么后果
        if not self.running:
            self._started.is_set = lambda: False
        else:
            self._started.is_set = lambda: True
        super().start()

    def put_task(self, task: _Task):
        assert isinstance(task, _Task)
        self.tasks.put(task)
        if not self.running:
            self.start()


class Action:  # pylint:disable=too-many-instance-attributes
    '''
    :param qq_or_bot: qq号或者机器人实例(`IOTBOT`)
    :param queue: 是否开启队列，开启后任务将按顺序发送并延时指定时间，此参数与`queue_delay`对应
                  启用后，发送方法`没有返回值`
    :param queue_delay: 与`队列`对应, 开启队列时发送每条消息间的延时, 保持默认即可
    :param timeout: 等待IOTBOT响应时间和发送请求的延时
    :param api_path: 方法路径
    :param port: 端口
    :param host: ip
    '''

    def __init__(self,
                 qq_or_bot: Union[int, IOTBOT] = None,
                 queue: bool = False,
                 queue_delay: Union[int, float] = 1.1,
                 timeout: int = 15,
                 api_path: str = '/v1/LuaApiCaller',
                 port: int = 8888,
                 host: str = 'http://127.0.0.1'):
        self.timeout = timeout
        self.api_path = api_path
        self.port = config.port or port
        self.host = config.host or host
        if isinstance(qq_or_bot, IOTBOT):
            self.bind_bot(qq_or_bot)
        else:
            self.qq = int(qq_or_bot)

        self.s = requests.Session()

        # 任务队列
        self._use_queue = queue
        self._send_thread = _SendThread(queue_delay)
        self._send_thread.setDaemon(True)

    def bind_bot(self, bot: IOTBOT):
        """绑定机器人"""
        self.qq = bot.qq[0]
        self.port = bot.port
        self.host = bot.host

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

    def send_private_text_msg(self, toUser: int, content: str, groupid: int,
                              timeout=5, **kwargs) -> dict:
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

    def send_private_voice_msg(self, toUser: int, groupid, voiceUrl='', voiceBase64Buf='',
                               timeout=5, **kwargs) -> dict:
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
        return self.baseSender('POST', 'SearchGroup', {"Content": content, "Page": page},
                               timeout, **kwargs)

    def get_user_info(self, userID: int, timeout=5, **kwargs) -> dict:
        '''获取用户信息'''
        return self.baseSender('POST', 'GetUserInfo', {'UserID': userID, 'GroupID': 0},
                               timeout, **kwargs)

    def get_cookies(self, timeout=2, **kwargs) -> dict:
        """获取cookies"""
        return self.baseSender('GET', 'GetUserCook', timeout=timeout, **kwargs)

    def get_group_list(self, timeout=5, **kwargs) -> dict:
        """获取群组列表"""
        return self.baseSender('POST', 'GetGroupList', {"NextToken": ""}, timeout, **kwargs)

    def get_group_admin_list(self, groupid: int, timeout=5, **kwargs) -> List[dict]:
        """获取群管理员列表"""
        members = self.get_group_user_list(groupid, timeout, **kwargs)
        return [member for member in members if member['GroupAdmin'] == 1]

    def get_group_all_admin_list(self, groupid: int, timeout=5, **kwargs) -> List[dict]:
        """群管理列表+群主"""
        owner = None
        for group in self.get_group_list(timeout)['TroopList']:
            if group['GroupId'] == groupid:
                owner = group['GroupOwner']
                break
        members = self.get_group_user_list(groupid, timeout, **kwargs)
        return [member for member in members if member['GroupAdmin'] == 1 or member['MemberUin'] == owner]

    def get_group_user_list(self, groupid: int, timeout=5, **kwargs) -> Generator[dict, None, None]:
        """获取群成员列表"""
        LastUin = 0
        while True:
            data = self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": LastUin},
                                   timeout, **kwargs)
            LastUin = data['LastUin']  # 上面请求失败会返回空字典。但是这里不处理错误, 必须正常抛出
            for member in data['MemberList']:
                yield member
            if LastUin == 0:
                break
            time.sleep(0.8)

    def set_unique_title(self, groupid: int, userid: int, Title: str, timeout=5, **kwargs) -> dict:
        """设置群成员头衔"""
        return self.baseSender('POST', 'OidbSvc.0x8fc_2',
                               {"GroupID": groupid, "UserID": userid, "NewTitle": Title},
                               timeout, **kwargs)

    def modify_group_card(self, userID: int, groupID: int, newNick: str, timeout=5, **kwargs) -> dict:
        '''修改群名片
        :params userID: 修改的QQ号
        :params groupID: 群号
        :params newNick: 新群名片
        '''
        data = {'UserID': userID, 'GroupID': groupID, 'NewNick': newNick}
        return self.baseSender('POST', 'ModifyGroupCard', data, timeout, **kwargs)

    def refresh_keys(self, timeout=20) -> bool:
        '''刷新key二次登陆, 成功返回True， 失败返回False'''
        try:
            rep = self.s.get(f'{self.host}:{self.port}/v1/RefreshKeys?qq={self.qq}', timeout=timeout)
            if rep.json()['Ret'] == 'ok':
                return True
        except Exception:
            pass
        return False

    def get_balance(self) -> dict:
        '''获取QQ钱包余额'''
        # TODO
    #     return self.baseSender('GET', 'GetBalance', timeout=timeout, **kwargs)

    def get_status(self, timeout=20) -> dict:
        '''获取机器人状态'''
        rep = self.s.get('{self.host}:{self.port}/v1/ClusterInfo', timeout=timeout)
        return rep.json()

    def send_single_red_bag(self) -> dict:
        '''发送群/好友红包'''
        # TODO
        #data = {}
        # return self.baseSender('POST', 'SendSingleRed', data, timeout, **kwargs)

    def send_qzone_red_bag(self) -> dict:
        '''发送QQ空间红包'''
        # TODO
        #data = {}
        # return self.baseSender('POST', 'SendQzoneRed', data, timeout, **kwargs)

    def send_transfer(self) -> dict:
        '''支付转账'''
        # TODO
        #data = {}
        # return self.baseSender('POST', 'Transfer', data, timeout, **kwargs)

    def open_red_bag(self, OpenRedBag) -> dict:
        '''打开红包 传入红包数据结构'''
        # TODO
    #     return self.baseSender('POST', 'OpenRedBag', OpenRedBag, timeout, **kwargs)

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
            res = self.s.post(f'{self.host}:{self.port}/v1/Group/Announce?qq={self.qq}', data=data,
                              timeout=timeout, **kwargs)
            return res.json()
        except Exception:
            return {}

    def deal_friend(self, Action: int) -> dict:
        """处理好友请求"""
        # TODO
        # --Action 1 忽略 2 同意 3 拒绝
        # data = {
        #     'Action':Action
        # }
        # return self.baseSender('POST', 'DealFriend', data, timeout, **kwargs)

    def deal_group(self, Action: int) -> dict:
        '''处理群邀请'''
        # TODO
        # --Action 14 忽略 1 同意 21 拒绝
        # data = {
        #     'Action':Action
        # }
        # return self.baseSender('POST', 'AnswerInviteGroup', data, timeout, **kwargs)

    def all_shut_up_on(self, groupid, timeout=20, **kwargs) -> dict:
        """开启全员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x89a_0', {"GroupID": groupid, "Switch": 1},
                               timeout, **kwargs)

    def all_shut_up_off(self, groupid, timeout=20, **kwargs) -> dict:
        """关闭全员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x89a_0', {"GroupID": groupid, "Switch": 0},
                               timeout, **kwargs)

    def you_shut_up(self, groupid, userid, shut_time=0, timeout=20, **kwargs) -> dict:
        """群成员禁言"""
        return self.baseSender('POST', 'OidbSvc.0x570_8',
                               {"GroupID": groupid, "ShutUpUserID": userid, "ShutTime": shut_time},
                               timeout, **kwargs)

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

    def set_group_admin(self, groupID: int, userID: int, timeout=10, **kwargs) -> dict:
        '''设置群管理员'''
        return self.baseSender('POST', 'OidbSvc.0x55c_1',
                               {"GroupID": groupID, "UserID": userID, "Flag": 1},
                               timeout, **kwargs)

    def cancel_group_admin(self, groupID: int, userID: int, timeout=10, **kwargs) -> dict:
        '''取消群管理员'''
        return self.baseSender('POST', 'OidbSvc.0x55c_1',
                               {"GroupID": groupID, "UserID": userID, "Flag": 0},
                               timeout, **kwargs)

    def repost_video_to_group(self, groupID: int, forwordBuf: str, timeout=10, **kwargs) -> dict:
        '''转发视频到群聊'''
        data = {
            "toUser": groupID,
            "sendToType": 2,
            "sendMsgType": "ForwordMsg",
            "content": "",
            "groupid": 0,
            "atUser": 0,
            "forwordBuf": forwordBuf,
            "forwordField": 19
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def repost_video_to_friend(self, userID: int, forwordBuf: str, timeout=10, **kwargs) -> dict:
        '''转发视频给好友'''
        data = {
            "toUser": userID,
            "sendToType": 1,
            "sendMsgType": "ForwordMsg",
            "content": "",
            "groupid": 0,
            "atUser": 0,
            "forwordBuf": forwordBuf,
            "forwordField": 19
        }
        return self.baseSender('POST', 'SendMsg', data, timeout, **kwargs)

    def get_login_qrcode(self) -> str:
        '''返回登录二维码的base64'''
        try:
            resp = self.s.get(
                '{}:{}/v1/Login/GetQRcode'.format(self.host, self.port), timeout=10)
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
                   bot_qq: int = None,
                   **kwargs) -> dict:
        """
        :param method: 请求方法
        :param funcname: 请求类型
        :param data: post的数据
        :param timeout: 发送请求等待响应的时间
        :param api_path: 默认为/v1/LuaApiCaller
        :param iot_timeout: IOT端处理请求等待的时间
        :param bot_qq: 机器人QQ

        :return: iotbot端返回的json数据(字典)，其他情况一律返回空字典
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
        if self._use_queue:
            self._send_thread.put_task(_Task(
                target=job,
                callback=kwargs.get('callback')
            ))
            return None
        return job()

    def _baseSender(self,
                    method: str,
                    funcname: str,
                    data: dict = None,
                    timeout: int = None,
                    api_path: str = None,
                    iot_timeout: int = None,
                    bot_qq: int = None) -> dict:
        params = {
            'funcname': funcname,
            'timeout': iot_timeout or self.timeout,
            'qq': bot_qq or self.qq
        }
        if data is None:
            data = {}
        try:
            rep = self.s.request(
                method=method,
                url='{}:{}{}'.format(self.host, self.port, api_path or self.api_path),
                headers={'Content-Type': 'application/json'},
                params=params,
                json=data,
                timeout=timeout or self.timeout
            )
            if rep.status_code != 200:
                logger.error(f'HTTP响应码错误 => {rep.status_code}')
                return {}
            response = rep.json() or {}  # 什么时候rep.json()会是None? 0.o
            self._report_response(response)
            return response
        except Exception as e:
            if isinstance(e, Timeout):
                logger.warning('响应超时，但不代表处理未成功, 结果未知!')
            else:
                logger.error(f'出现错误 => {traceback.format_exc()}')
            return {}

    def _report_response(self, response):
        if 'Ret' in response:
            ret = response['Ret']
            if ret == 0:
                return
            if ret == 241:
                logger.error(f'请求频繁 => {response}')
            else:
                logger.error(f'请求发送成功, 但处理失败 => {response}')
