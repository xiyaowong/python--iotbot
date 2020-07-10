# pylint: disable=protected-access
"""
封装部分最常用发送操作
"""

import base64
import sys

from .action import Action
from .model import FriendMsg, GroupMsg


def Text(text: str,
         at=False):
    """发送文字
    :param text: 文字内容
    :param at:是否艾特发送该消息的用户
    """
    # 查找消息上下文 `ctx`变量
    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if ('ctx' in upper_locals and
            type(upper_locals['ctx']) in [GroupMsg, FriendMsg]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ###################################################
    if isinstance(ctx, GroupMsg):
        return Action(ctx.CurrentQQ).send_group_text_msg(
            ctx.FromGroupId,
            content=text,
            atUser=ctx.FromUserId if at else 0
        )
    ##################################################
    elif isinstance(ctx, FriendMsg):
        return Action(ctx.CurrentQQ).send_friend_text_msg(
            ctx.FromUin,
            text
        )
    else:
        raise BaseException('经支持群消息和好友消息接收函数内调用')


def Picture(pic_url='',
            pic_base64='',
            pic_path=''):
    """发送图片
    :param pic_url: 图片链接
    :param pic_base64: 图片base64编码
    :param pic_path: 图片文件路径

    pic_url, pic_base64, pic_path必须给定一项
    """
    assert any([pic_url, pic_base64, pic_path])  # 必须给定一项

    # 查找消息上下文 `ctx`变量
    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if ('ctx' in upper_locals and
            type(upper_locals['ctx']) in [GroupMsg, FriendMsg]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ##################################################
    if isinstance(ctx, GroupMsg):
        if pic_url:
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picUrl=pic_url
            )
        elif pic_base64:
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picBase64Buf=pic_base64
            )
        elif pic_path:
            with open(pic_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_group_pic_msg(
                ctx.FromGroupId,
                picBase64Buf=b64
            )
        return None
    ##################################################
    elif isinstance(ctx, FriendMsg):
        if pic_url:
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picUrl=pic_url
            )
        elif pic_base64:
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picBase64Buf=pic_base64
            )
        elif pic_path:
            with open(pic_path, 'rb') as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picBase64Buf=b64
            )
        return None
    else:
        raise BaseException('经支持群消息和好友消息接收函数内调用')


def Voice(voice_url='',
          voice_base64='',
          voice_path=''):
    """发送语音
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
            type(upper_locals['ctx']) in [GroupMsg, FriendMsg]):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if type(v) in [GroupMsg, FriendMsg]:
                ctx = v
                break
    ##################################################
    if isinstance(ctx, GroupMsg):
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
    elif isinstance(ctx, FriendMsg):
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
