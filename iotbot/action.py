"""一些常用的方法

其中对于发送语音，图片的方法，建议将timeout设置很短，因为暂时发现这类请求因为需要文件上传操作，
响应时间会较长，而且目前来看，如果文件较大导致上传时间太长，IOTBOT端会报错, IOTBOT响应的结果一定是错误的,
不过发送去的操作是能正常完成的。
"""
import requests
from requests.exceptions import Timeout

from .client import IOTBOT
from .logger import Logger


class Action:
    """
    :params qq_or_bot: qq号或者机器人实例(`IOTBOT`)
    :params timeout: 等待IOTBOT响应时间，不是发送请求的延时
    :params log_file_path: 日志文件路径
    :params api_path: 方法路径
    """

    def __init__(self,
                 qq_or_bot=None,
                 timeout=10,
                 log_file_path=None,
                 api_path='/v1/LuaApiCaller',
                 port=8888,
                 host='http://127.0.0.1'):
        self.__timeout = timeout
        self.__api_path = api_path
        self.__port = port
        self.__host = host
        if isinstance(qq_or_bot, IOTBOT):
            self.bind_bot(qq_or_bot)
        else:
            self.qq = int(qq_or_bot)
        self.logger = Logger(log_file_path)

    def bind_bot(self, bot: IOTBOT):
        """绑定机器人"""
        self.qq = bot.qq
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
                             fileMd5='', timeout=5, **kwargs) -> dict:
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
        """发送群Json类型信息"""
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
        """获取用户信息"""
        return self.baseSender('POST', 'GetUserInfo', {'UserID': userID, 'GroupID': 0}, timeout, **kwargs)

    def get_cookies(self, timeout=2, **kwargs) -> dict:
        """获取cookies"""
        return self.baseSender('GET', 'GetUserCook', timeout=timeout, **kwargs)

    def get_group_list(self, timeout=5, **kwargs) -> dict:
        """获取群组列表"""
        return self.baseSender('POST', 'GetGroupList', {"NextToken": ""}, timeout, **kwargs)

    def get_group_user_list(self, groupid: int, timeout=5, **kwargs) -> dict:
        """获取群成员列表"""
        return self.baseSender('POST', 'GetGroupUserList', {"GroupUin": groupid, "LastUin": 0}, timeout, **kwargs)

    def set_unique_title(self, groupid: int, userid: int, Title: str, timeout=1, **kwargs) -> dict:
        """设置群成员头衔"""
        return self.baseSender('POST', 'OidbSvc.0x8fc_2', {"GroupID": groupid, "UserID": userid, "NewTitle": Title},
                               timeout, **kwargs)

    def modify_group_card(self, userID: int, groupID: int, newNick: str, timeout=5, **kwargs) -> dict:
        """修改群名片

        :params userID: 修改的QQ号
        :params groupID: 群号
        :params newNick: 新群名片

        """
        data = {
            'UserID': userID,
            'GroupID': groupID,
            'NewNick': newNick
        }
        return self.baseSender('POST', 'ModifyGroupCard', data, timeout, **kwargs)

    def get_friend_deal(self, data: dict, timeout=5, **kwargs) -> dict:
        """处理好友请求"""
        # data = {'UserID': 123456789,
        #         'FromType': 1234,
        #         'Field_9': 1592883849000000,
        #         'Content': '收到好友请求 内容我是炫耘来源来自QQ号查找',
        #         'FromGroupId': 0,
        #         'FromGroupName': '',
        #         'Action': 11}
        return self.baseSender('POST', 'DealFriend', data, timeout, **kwargs)

    def get_group_answer_invite(self, data: dict, timeout=5, **kwargs) -> dict:
        """处理群邀请"""
        # data = {"Seq": seq,
        #         "Type": 1,
        #         "MsgTypeStr": "邀请加群",
        #         "Who": 123456789,
        #         "WhoName": "QQ棒棒冰",
        #         "MsgStatusStr": "",
        #         "Flag_7": 123,
        #         "Flag_8": 123,
        #         "GroupId": 123456789,
        #         "GroupName": "123",
        #         "InviteUin": 123456789,
        #         "InviteName": "123",
        #         "Action": zx
        #         }
        return self.baseSender('POST', 'AnswerInviteGroup', data, timeout, **kwargs)

    def get_open_redbag(self, data: dict, timeout=5, **kwargs):
        """打开红包"""
        return self.baseSender('POST', 'OpenRedBag', data, timeout, **kwargs)

    # def get_friend_add(self, userID: int, timeout=5, **kwargs) -> dict:
    #     """添加好友"""
    #     data = {"AddUserUid": 123456789, "FromGroupID": 123456789, "AddFromSource": 2004, "Content": "加好友，互助浇水"}
    #     return self.baseSender('POST', 'AddQQUser', data, timeout, **kwargs)

    def get_group_mgr(self,actiontype: int, toUser: int, atUser=0, content='', timeout=5, **kwargs):
        """QQ群功能包加群 拉人 踢群 退群
        # ActionType = 8 拉人入群 -->{"ActionType": 8, "GroupID": 123456, "ActionUserID": 987654, "Content": ""}
        # ActionType = 1 加入群聊 -->{"ActionType": 1, "GroupID": 123456, "ActionUserID": 0, "Content": "你好通过一下"}
        # ActionType = 2 退出群聊 -->{"ActionType": 2, "GroupID": 123456, "ActionUserID": 0, "Content": ""}
        # ActionType = 3 移出群聊 -->{"ActionType": 3, "GroupID": 123456, "ActionUserID": 987654, "Content": ""}
        """
        data = {
            "ActionType": actiontype,  # 群操作类型
            "GroupID": toUser,  # 目标群ID
            "ActionUserID": atUser,  # 移除群的UserID
            "Content": content  # 加群理由
        }
        return self.baseSender('POST', 'GroupMgr', data, timeout, **kwargs)

    def get_qq_zan(self, atUser=0, timeout=5, **kwargs):
        """QQ赞"""
        data = {"UserID": atUser}
        return self.baseSender('POST', 'OpenRedBag', data, timeout, **kwargs)

    def refresh_keys(self) -> bool:
        """刷新key二次登陆, 成功返回True， 失败返回False"""
        try:
            rep = requests.get(f'{self.__host}:8888/v1/RefreshKeys?qq={self.qq}', timeout=20)
            if rep.json()['Ret'] == 'ok':
                return True
        except Exception:
            pass
        return False

    def baseSender(self,
                   method: str,
                   funcname: str,
                   data: dict = None,
                   timeout: int = None,
                   api_path: str = None,
                   iot_timeout: int = None,
                   bot_qq: int = None) -> dict:
        """
        :param method: 请求方法
        :param funcname: 请求类型
        :param data: post的数据
        :param timeout: 发送请求等待响应的时间
        :param api_path: 默认为/v1/LuaApiCaller
        :param iot_timeout: IOT端处理请求等待的时间
        :param bot_qq: 机器人QQ
        """

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
            rep.raise_for_status()
            if 'Ret' in rep.text and not rep.json()['Ret'] == 0:
                self.logger.error(f'请求发送成功, 但处理失败: {rep.json()}')
            return rep.json()
        except Exception as e:
            if isinstance(e, Timeout):
                self.logger.warning('响应超时，但不代表处理未成功, 结果未知!')
                return {}
            self.logger.error(f'出现错误: {e}')
            return {}

