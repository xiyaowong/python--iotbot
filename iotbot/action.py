"""一些常用的方法

其中对于发送语音，图片的方法，建议将timeout设置很短，因为暂时发现这类请求因为需要文件上传操作，
响应时间会较长，而且目前来看，如果文件较大导致上传时间太长，IOTBOT端会报错, IOTBOT响应的结果一定是错误的,
不过发送去的操作是能正常完成的。
"""
import sys

import requests
from requests.exceptions import Timeout

from .client import IOTBOT


class Action:
    def __init__(self,
                 qq='',
                 timeout=10,
                 api_path='/v1/LuaApiCaller',
                 port=8888,
                 host='http://127.0.0.1'):
        self.qq = qq
        self.__timeout = timeout
        self.__api_path = api_path
        self.__port = port
        self.__host = host

    def bind_bot(self, bot: IOTBOT):
        """绑定机器人"""
        self.qq = bot.qq
        self.__port = bot.port
        self.__host = bot.host

    def send_friend_text_msg(self, toUser: int, content: str, timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def get_user_list(self) -> dict:
        """获取好友列表"""
        return self.baseSender('post', 'GetQQUserList', {"StartIndex": 0})

    def send_friend_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf='', timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_friend_pic_msg(self, toUser, content='', picUrl='', picBase64Buf='', fileMd5='', flashPic=False, timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_group_text_msg(self, toUser: int, content='', atUser=0) -> dict:
        """发送群文字消息"""
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data)

    def send_group_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf='', timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_group_pic_msg(self, toUser: int, picUrl='', flashPic=False, atUser=0, content='', picBase64Buf='', fileMd5='', timeout=3):
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_private_text_msg(self, toUser: int, content: str, groupid: int) -> dict:
        """发送私聊文字消息"""
        data = {
            "toUser": toUser,
            "sendToType": 3,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": groupid,
            "atUser": 0
        }
        return self.baseSender('POST', 'SendMsg', data)

    def send_private_voice_msg(self, toUser: int, groupid, voiceUrl='', voiceBase64Buf='', timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_private_pic_msg(self, toUser, groupid, picUrl='', picBase64Buf='', content='', fileMd5='', timeout=5) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data, timeout)

    def send_group_json_msg(self, toUser: int, content='', atUser=0) -> dict:
        """发送群Json类型信息"""
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "JsonMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data)

    def search_group(self, content, page=0) -> dict:
        """搜索群组"""
        return self.baseSender('POST', 'SearchGroup', {"Content": content, "Page": page})

    def get_cookies(self) -> dict:
        """获取cookies"""
        return self.baseSender('GET', 'GetUserCook')

    def get_group_list(self) -> dict:
        """获取群组列表"""
        return self.baseSender('POST', 'GetGroupList', {"NextToken": ""})

    def get_group_user_list(self, groupid: int) -> dict:
        """获取群成员列表"""
        return self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": 0})

    def baseSender(self, method: str, funcname: str, data=None, timeout: int = None, api_path=None) -> dict:
        """
        :param method: 请求方法
        :param funcname: 请求类型
        :param data: post的数据
        :param timeout: 请求等待响应的时间
        :param api_path: 默认为/v1/LuaApiCaller
        """
        params = {
            'funcname': funcname,
            'timeout': timeout or self.__timeout,
            'qq': self.qq
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
            rep.raise_for_status()
            if 'Ret' in rep.text and not rep.json()['Ret'] == 0:
                sys.stdout.write(f'请求发送成功, 但事件响应失败: {rep.json()}')
            return rep.json()
        except Exception as e:
            if isinstance(e, Timeout):
                sys.stdout.write('响应超时，但不代表处理未成功,结果未知!')
                return {}
            sys.stderr.write(f'出现错误: {e}')
            return {}
