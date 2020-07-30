# pylint: disable=protected-access
"""
封装部分最常用发送操作
"""

import base64
import sys

from .action import Action
from .model import FriendMsg
from .model import GroupMsg
from .refine_message import _AtGroupMsg
from .refine_message import _PicFriendMsg
from .refine_message import _PicGroupMsg
from .refine_message import _RedBagFriendMsg
from .refine_message import _RedBagGroupMsg
from .refine_message import _VoiceFriendMsg
from .refine_message import _VoiceGroupMsg


def Text(text: str,
         at=False):
    """发送文字 经支持群消息和好友消息接收函数内调用
    :param text: 文字内容
    :param at:是否艾特发送该消息的用户
    """
    text = str(text)
    # 查找消息上下文 `ctx`变量
    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if ('ctx' in upper_locals and
            type(upper_locals['ctx']) in [
                GroupMsg,
                FriendMsg,
                _AtGroupMsg,
                _PicFriendMsg,
                _PicGroupMsg,
                _RedBagFriendMsg,
                _RedBagGroupMsg,
                _VoiceFriendMsg,
                _VoiceGroupMsg
            ]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ###################################################
    if type(ctx) in [
        GroupMsg,
        _AtGroupMsg,
        _PicGroupMsg,
        _RedBagGroupMsg,
        _VoiceGroupMsg
    ]:
        return Action(ctx.CurrentQQ).send_group_text_msg(
            ctx.FromGroupId,
            content=text,
            atUser=ctx.FromUserId if at else 0
        )
    ##################################################
    elif type(ctx) in [
        FriendMsg,
        _PicFriendMsg,
        _RedBagFriendMsg,
        _VoiceFriendMsg,
    ]:
        return Action(ctx.CurrentQQ).send_friend_text_msg(
            ctx.FromUin,
            text
        )
    else:
        raise BaseException('经支持群消息和好友消息接收函数内调用')


def Picture(pic_url='',
            pic_base64='',
            pic_path='',
            content=''):
    """发送图片 经支持群消息和好友消息接收函数内调用
    :param pic_url: 图片链接
    :param pic_base64: 图片base64编码
    :param pic_path: 图片文件路径
    :param content: 包含的文字消息

    pic_url, pic_base64, pic_path必须给定一项
    """
    assert any([pic_url, pic_base64, pic_path])  # 必须给定一项

    # 查找消息上下文 `ctx`变量
    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if ('ctx' in upper_locals and
            type(upper_locals['ctx']) in [
                GroupMsg,
                FriendMsg,
                _AtGroupMsg,
                _PicFriendMsg,
                _PicGroupMsg,
                _RedBagFriendMsg,
                _RedBagGroupMsg,
                _VoiceFriendMsg,
                _VoiceGroupMsg
            ]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ##################################################
    if type(ctx) in [
        GroupMsg,
        _AtGroupMsg,
        _PicGroupMsg,
        _RedBagGroupMsg,
        _VoiceGroupMsg
    ]:
        if pic_url:
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picUrl=pic_url,
                content=content
            )
        elif pic_base64:
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picBase64Buf=pic_base64,
                content=content
            )
        elif pic_path:
            with open(pic_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picBase64Buf=b64,
                content=content
            )
        return None
    ##################################################
    elif type(ctx) in [
        FriendMsg,
        _PicFriendMsg,
        _RedBagFriendMsg,
        _VoiceFriendMsg,
    ]:
        if pic_url:
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picUrl=pic_url,
                content=content
            )
        elif pic_base64:
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picBase64Buf=pic_base64,
                content=content
            )
        elif pic_path:
            with open(pic_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picBase64Buf=b64,
                content=content
            )
        return None
    else:
        raise BaseException('经支持群消息和好友消息接收函数内调用')


def Voice(voice_url='',
          voice_base64='',
          voice_path=''):
    """发送语音 经支持群消息和好友消息接收函数内调用
    :param voice_url: 语音链接
    :param voice_base64: 语音base64编码
    :param voice_path: 语音文件路径

    voice_url, voice_base64, voice_path必须给定一项
    """
    assert any([voice_url, voice_base64, voice_path])  # 必须给定一项
    # 查找消息上下文 `ctx`变量
    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if ('ctx' in upper_locals and
            type(upper_locals['ctx']) in [
                GroupMsg,
                FriendMsg,
                _AtGroupMsg,
                _PicFriendMsg,
                _PicGroupMsg,
                _RedBagFriendMsg,
                _RedBagGroupMsg,
                _VoiceFriendMsg,
                _VoiceGroupMsg
            ]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ##################################################
    if type(ctx) in [
        GroupMsg,
        _AtGroupMsg,
        _PicGroupMsg,
        _RedBagGroupMsg,
        _VoiceGroupMsg
    ]:
        if voice_url:
            return Action(ctx.CurrentQQ).send_group_voice_msg(
                ctx.FromGroupId,
                voiceUrl=voice_url
            )
        elif voice_base64:
            return Action(ctx.CurrentQQ).send_group_voice_msg(
                ctx.FromGroupId,
                voiceBase64Buf=voice_base64
            )
        elif voice_path:
            with open(voice_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_group_voice_msg(
                ctx.FromGroupId,
                voiceBase64Buf=b64
            )
        return None
    ##################################################
    elif type(ctx) in [
        FriendMsg,
        _PicFriendMsg,
        _RedBagFriendMsg,
        _VoiceFriendMsg,
    ]:
        if voice_url:
            return Action(ctx.CurrentQQ).send_friend_voice_msg(
                ctx.FromUin,
                voiceUrl=voice_url
            )
        elif voice_base64:
            return Action(ctx.CurrentQQ).send_friend_voice_msg(
                ctx.FromUin,
                voiceBase64Buf=voice_base64
            )
        elif voice_path:
            with open(voice_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_friend_voice_msg(
                ctx.FromUin,
                voiceBase64Buf=b64
            )
        return None
    else:
        raise BaseException('经支持群消息和好友消息接收函数内调用')
