# pylint: disable=too-many-instance-attributes, super-init-not-called
"""进一步提取消息详细信息的函数"""
from typing import List

from .exceptions import ContextTypeError
from .model import EventMsg
from .model import FriendMsg
from .model import GroupMsg
from .utils import EventNames
from .utils import MsgTypes

try:
    import ujson as json
except Exception:
    import json


#############################Event begin########################################
class _EventMsg(EventMsg):
    def _carry_properties(self, ctx: EventMsg):
        self.message = ctx.message
        self.CurrentQQ = ctx.CurrentQQ

        self.data = ctx.data

        self.EventName = ctx.EventName
        self.EventData = ctx.EventData
        self.EventMsg = ctx.EventMsg

        self.Content = ctx.Content
        self.FromUin = ctx.FromUin
        self.MsgSeq = ctx.MsgSeq
        self.MsgType = ctx.MsgType
        self.ToUin = ctx.ToUin
        self.RedBaginfo = ctx.RedBaginfo


class _GroupRevokeEventMsg(_EventMsg):
    """群成员撤回消息事件"""

    def __init__(self, ctx: EventMsg):
        event_data = ctx.EventData
        self.AdminUserID: int = event_data.get('AdminUserID')
        self.GroupID: int = event_data.get('GroupID')
        self.MsgRandom: int = event_data.get('MsgRandom')
        self.MsgSeq: int = event_data.get('MsgSeq')
        self.UserID: int = event_data.get('UserID')
        super()._carry_properties(ctx)


class _GroupExitEventMsg(_EventMsg):
    """群成员退出群聊事件"""

    def __init__(self, ctx: EventMsg):
        self.UserID = ctx.EventData.get('UserID')
        super()._carry_properties(ctx)


class _GroupJoinEventMsg(_EventMsg):
    """某人进群事件"""

    def __init__(self, ctx: EventMsg):
        e_data = ctx.EventData
        self.InviteUin: int = e_data.get('InviteUin')
        self.UserID: int = e_data.get('UserID')
        self.UserName: str = e_data.get('UserName')
        super()._carry_properties(ctx)


class _FriendRevokeEventMsg(_EventMsg):
    """好友撤回消息事件"""

    def __init__(self, ctx: EventMsg):
        self.MsgSeq = ctx.EventData.get('MsgSeq')
        self.UserID = ctx.EventData.get('UserID')
        super()._carry_properties(ctx)


class _FriendDeleteEventMsg(_EventMsg):
    """删除好友事件"""

    def __init__(self, ctx: EventMsg):
        self.UserID: int = ctx.EventData.get('UserID')
        super()._carry_properties(ctx)


class _GroupAdminsysnotifyEventMsg(_EventMsg):
    """QQ群系统消息通知(加群申请在这里面"""

    def __init__(self, ctx: EventMsg):
        edata = ctx.EventData
        self.Type: int = edata.get('Type')  # 事件类型
        self.MsgTypeStr: str = edata.get('MsgTypeStr')  # 消息类型
        self.MsgStatusStr: str = edata.get('MsgStatusStr')  # 消息类型状态
        self.Who: int = edata.get('Who')  # 触发消息的对象
        self.WhoName: int = edata.get('WhoName')  # 触发消息的对象昵称
        self.GroupID: int = edata.get('GroupId')  # 来自群
        self.GroupName: str = edata.get('GroupName')  # 群名
        self.ActionUin: int = edata.get('ActionUin')  # 邀请人(处理人)
        self.ActionName: str = edata.get('ActionName')  # 邀请人(处理人)昵称
        self.ActionGroupCard: str = edata.get('ActionGroupCard')  # 邀请人(处理人)群名片
        self.Action: str = edata.get('Action')  # 加群理由 11 agree 14 忽略 12/21 disagree
        self.Content: int = edata.get('Content')
        super()._carry_properties(ctx)


class _GroupShutEventMsg(_EventMsg):
    """群禁言事件"""

    def __init__(self, ctx: EventMsg):
        self.GroupID: int = ctx.EventData.get('GroupID')
        self.ShutTime: int = ctx.EventData.get('ShutTime')
        self.UserID: int = ctx.EventData.get('UserID')
        super()._carry_properties(ctx)


class _GroupAdminEventMsg(_EventMsg):
    """管理员变更事件"""

    def __init__(self, ctx: EventMsg):
        self.Flag: int = ctx.EventData.get('Flag')
        self.GroupID: int = ctx.EventData.get('GroupID')
        self.UserID: int = ctx.EventData.get('UserID')
        super()._carry_properties(ctx)


def refine_group_revoke_event_msg(ctx: EventMsg) -> _GroupRevokeEventMsg:
    """群成员撤回消息事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_REVOKE:
        return _GroupRevokeEventMsg(ctx)
    return None


def refine_group_exit_event_msg(ctx: EventMsg) -> _GroupExitEventMsg:
    """群成员退出群聊事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_EXIT:
        return _GroupExitEventMsg(ctx)
    return None


def refine_group_join_event_msg(ctx: EventMsg) -> _GroupJoinEventMsg:
    """某人进群事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_JOIN:
        return _GroupJoinEventMsg(ctx)
    return None


def refine_friend_revoke_event_msg(ctx: EventMsg) -> _FriendRevokeEventMsg:
    """好友撤回消息事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_FRIEND_REVOKE:
        return _FriendRevokeEventMsg(ctx)
    return None


def refine_friend_delete_event_msg(ctx: EventMsg) -> _FriendDeleteEventMsg:
    """删除好友事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_FRIEND_DELETE:
        return _FriendDeleteEventMsg(ctx)
    return None


def refine_group_adminsysnotify_event_msg(ctx: EventMsg) -> _GroupAdminsysnotifyEventMsg:
    """加群申请"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_ADMINSYSNOTIFY:
        return _GroupAdminsysnotifyEventMsg(ctx)
    return None


def refine_group_shut_event_msg(ctx: EventMsg) -> _GroupShutEventMsg:
    """群禁言事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_SHUT:
        return _GroupShutEventMsg(ctx)
    return None


def refine_group_admin_event_msg(ctx: EventMsg) -> _GroupAdminEventMsg:
    """管理员变更事件"""
    if not isinstance(ctx, EventMsg):
        raise ContextTypeError('Expected `EventMsg`, but got `%s`' % ctx.__class__)
    if ctx.EventName == EventNames.ON_EVENT_GROUP_ADMIN:
        return _GroupAdminEventMsg(ctx)
    return None
#############################Event end##########################################


#############################Group start########################################
class _GroupMsg(GroupMsg):
    def _carry_properties(self, ctx: GroupMsg):
        self.message = ctx.message
        self.CurrentQQ = ctx.CurrentQQ

        self.data = ctx.data

        self.FromGroupId: int = ctx.FromGroupId
        self.FromGroupName: str = ctx.FromGroupId
        self.FromUserId: int = ctx.FromUserId
        self.FromNickName: str = ctx.FromNickName
        self.Content: str = ctx.Content
        self.MsgType: str = ctx.MsgType
        self.MsgTime: int = ctx.MsgTime
        self.MsgSeq: int = ctx.MsgSeq
        self.MsgRandom: int = ctx.MsgRandom
        self.RedBaginfo: dict = ctx.RedBaginfo


class _VoiceGroupMsg(_GroupMsg):
    """群语音消息"""

    def __init__(self, ctx: GroupMsg):
        voice_data = json.loads(ctx.Content)
        self.VoiceUrl: str = voice_data['Url']
        self.Tips: str = voice_data['Tips']
        super()._carry_properties(ctx)


class _VideoGroupMsg(_GroupMsg):
    """群视频消息"""

    def __init__(self, ctx: GroupMsg):
        video_data = json.loads(ctx.Content)
        self.ForwordBuf: str = video_data['ForwordBuf']
        self.ForwordField: int = video_data['ForwordField']
        self.Tips: str = video_data['Tips']
        self.VideoMd5: str = video_data['VideoMd5']
        self.VideoSize: str = video_data['VideoSize']
        self.VideoUrl: str = video_data['VideoUrl']
        super()._carry_properties(ctx)


class _PicGroupMsg(_GroupMsg):
    """群图片/表情包消息"""

    def __init__(self, ctx: GroupMsg):
        pic_data = json.loads(ctx.Content)
        self.GroupPic: List[dict] = pic_data['GroupPic']
        self.Tips: str = pic_data['Tips']
        super()._carry_properties(ctx)


class _AtGroupMsg(_GroupMsg):
    def __init__(self, ctx: GroupMsg):
        super()._carry_properties(ctx)


class _RedBagGroupMsg(_GroupMsg):
    """群红包消息"""

    def __init__(self, ctx: GroupMsg):
        redbag_info = ctx.RedBaginfo
        self.RedBag_Authkey: str = redbag_info.get('Authkey')
        self.RedBag_Channel: int = redbag_info.get('Channel')
        self.RedBag_Des: str = redbag_info.get('Des')
        self.RedBag_FromType: int = redbag_info.get('FromType')
        self.RedBag_FromUin: int = redbag_info.get('FromUin')
        self.RedBag_Listid: str = redbag_info.get('Listid')
        self.RedBag_RedType: int = redbag_info.get('RedType')
        self.RedBag_StingIndex: str = redbag_info.get('StingIndex')
        self.RedBag_Tittle: str = redbag_info.get('Tittle')
        self.RedBag_Token_17_2: str = redbag_info.get('Token_17_2')
        self.RedBag_Token_17_3: str = redbag_info.get('Token_17_3')
        super()._carry_properties(ctx)


def refine_voice_group_msg(ctx: GroupMsg) -> _VoiceGroupMsg:
    """群语音消息"""
    if not isinstance(ctx, GroupMsg):
        raise ContextTypeError('Expected `GroupMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.VoiceMsg:
        return _VoiceGroupMsg(ctx)
    return None


def refine_video_group_msg(ctx: GroupMsg) -> _VideoGroupMsg:
    """群视频消息"""
    if not isinstance(ctx, GroupMsg):
        raise ContextTypeError('Expected `GroupMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.VideoMsg:
        return _VideoGroupMsg(ctx)
    return None


def refine_pic_group_msg(ctx: GroupMsg) -> _PicGroupMsg:
    """群图片/表情包消息"""
    if not isinstance(ctx, GroupMsg):
        raise ContextTypeError('Expected `GroupMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.PicMsg:
        return _PicGroupMsg(ctx)
    return None


def refine_RedBag_group_msg(ctx: GroupMsg) -> _RedBagGroupMsg:
    """群红包消息"""
    if not isinstance(ctx, GroupMsg):
        raise ContextTypeError('Expected `GroupMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.RedBagMsg:
        return _RedBagGroupMsg(ctx)
    return None
#############################Group end##########################################


#############################Friend start#######################################
class _FriendMsg(FriendMsg):
    def _carry_properties(self, ctx: FriendMsg):
        self.message = ctx.message
        self.CurrentQQ = ctx.CurrentQQ

        self.data = ctx.data

        self.FromUin: int = ctx.FromUin
        self.ToUin: int = ctx.ToUin
        self.MsgType: str = ctx.MsgType
        self.MsgSeq: int = ctx.MsgSeq
        self.Content: str = ctx.Content
        self.RedBaginfo: dict = ctx.RedBaginfo


class _VoiceFriendMsg(_FriendMsg):
    """好友语音消息"""

    def __init__(self, ctx: FriendMsg):
        voice_data = json.loads(ctx.Content)
        self.VoiceUrl: str = voice_data['Url']
        self.Tips: str = voice_data['Tips']
        super()._carry_properties(ctx)


class _VideoFriendMsg(_FriendMsg):
    """好友视频消息"""

    def __init__(self, ctx: FriendMsg):
        video_data = json.loads(ctx.Content)
        self.ForwordBuf: str = video_data['ForwordBuf']
        self.ForwordField: int = video_data['ForwordField']
        self.Tips: str = video_data['Tips']
        self.VideoMd5: str = video_data['VideoMd5']
        self.VideoSize: str = video_data['VideoSize']
        self.VideoUrl: str = video_data['VideoUrl']
        super()._carry_properties(ctx)


class _PicFriendMsg(_FriendMsg):
    """好友图片/表情包消息"""

    def __init__(self, ctx: FriendMsg):
        pic_data = json.loads(ctx.Content)
        self.GroupPic: List[dict] = pic_data['FriendPic']
        self.Tips: str = pic_data['Tips']
        super()._carry_properties(ctx)


class _RedBagFriendMsg(_FriendMsg):
    """好友红包消息"""

    def __init__(self, ctx: FriendMsg):
        redbag_info = ctx.RedBaginfo
        self.RedBag_Authkey: str = redbag_info.get('Authkey')
        self.RedBag_Channel: int = redbag_info.get('Channel')
        self.RedBag_Des: str = redbag_info.get('Des')
        self.RedBag_FromType: int = redbag_info.get('FromType')
        self.RedBag_FromUin: int = redbag_info.get('FromUin')
        self.RedBag_Listid: str = redbag_info.get('Listid')
        self.RedBag_RedType: int = redbag_info.get('RedType')
        self.RedBag_StingIndex: str = redbag_info.get('StingIndex')
        self.RedBag_Tittle: str = redbag_info.get('Tittle')
        self.RedBag_Token_17_2: str = redbag_info.get('Token_17_2')
        self.RedBag_Token_17_3: str = redbag_info.get('Token_17_3')
        super()._carry_properties(ctx)


def refine_voice_friend_msg(ctx: FriendMsg) -> _VoiceFriendMsg:
    """好友语音消息"""
    if not isinstance(ctx, FriendMsg):
        raise ContextTypeError('Expected `FriendMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.VoiceMsg:
        return _VoiceFriendMsg(ctx)
    return None


def refine_video_friend_msg(ctx: FriendMsg) -> _VideoFriendMsg:
    """好友视频消息"""
    if not isinstance(ctx, FriendMsg):
        raise ContextTypeError('Expected `FriendMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.VideoMsg:
        return _VideoFriendMsg(ctx)
    return None


def refine_pic_friend_msg(ctx: FriendMsg) -> _PicFriendMsg:
    """好友图片/表情包消息"""
    if not isinstance(ctx, FriendMsg):
        raise ContextTypeError('Expected `FriendMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.PicMsg:
        return _PicFriendMsg(ctx)
    return None


def refine_RedBag_friend_msg(ctx: FriendMsg) -> _RedBagFriendMsg:
    """好友红包消息"""
    if not isinstance(ctx, FriendMsg):
        raise ContextTypeError('Expected `FriendMsg`, but got `%s`' % ctx.__class__)
    if ctx.MsgType == MsgTypes.RedBagMsg:
        return _RedBagFriendMsg(ctx)
    return None
#############################Friend end#########################################
