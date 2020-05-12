import sys

import requests

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
        self.qq = bot.qq
        self.__port = bot.port
        self.__host = bot.host

    def send_friend_text_msg(self, toUser: int, content: str) -> dict:
        data = {
            "toUser": toUser,
            "sendToType": 1,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": 0,
            "atUser": 0,
            "replayInfo": None
        }
        print(data)
        return self.baseSender('POST', 'SendMsg', data)

    def get_user_list(self) -> dict:
        """获取好友列表"""
        return self.baseSender('post', 'GetQQUserList', {"StartIndex": 0})

    def send_friend_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf='') -> dict:
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
        return self.baseSender('POST', 'SendMsg', data)

    def send_friend_pic_msg(self, toUser, content='', picUrl='', picBase64Buf='', fileMd5='', flashPic=False) -> dict:
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
        return self.baseSender('POST', 'SendMsg', data)

    def send_group_text_msg(self, toUser: int, content='', atUser=0):
        data = {
            "toUser": toUser,
            "sendToType": 2,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": 0,
            "atUser": atUser
        }
        return self.baseSender('POST', 'SendMsg', data)

    def send_group_voice_msg(self, toUser, voiceUrl='', voiceBase64Buf=''):
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
        return self.baseSender('POST', 'SendMsg', data)

    def send_group_pic_msg(self, toUser: int, picUrl='', flashPic=False, atUser=0, content='', picBase64Buf='', fileMd5=''):
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
        return self.baseSender('POST', 'SendMsg', data)

    def send_private_text_msg(self, toUser: int, content: str, groupid: int) -> dict:
        data = {
            "toUser": toUser,
            "sendToType": 3,
            "sendMsgType": "TextMsg",
            "content": content,
            "groupid": groupid,
            "atUser": 0
        }
        return self.baseSender('POST', 'SendMsg', data)

    def send_private_voice_msg(self, toUser: int, groupid, voiceUrl='', voiceBase64Buf=''):
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
        return self.baseSender('POST', 'SendMsg', data)

    def send_private_pic_msg(self, toUser, groupid, picUrl='', picBase64Buf='', content='', fileMd5=''):
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
        return self.baseSender('POST', 'SendMsg', data)

    def get_cookies(self):
        return self.baseSender('GET', 'GetUserCook')

    def baseSender(self, method: str, funcname: str, data=None, timeout: int = None):
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
                url=f'{self.__host}:{self.__port}{self.__api_path}',
                headers={'Content-Type': 'application/json'},
                params=params,
                json=data,
                timeout=self.__timeout
            )
            rep.raise_for_status()
            if not rep.json()['Ret'] == 0:
                sys.stdout.write(f'请求发送成功, 但事件响应失败: {rep.json()}')
            return rep.json()
        except Exception as e:
            sys.stderr.write(f'出现错误: {e}')
            return {}
