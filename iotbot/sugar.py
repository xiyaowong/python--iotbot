# pylint: disable=protected-access
"""封装部分最常用发送操作
使用的前提:
    已经通过.iotbot.json配置好地址和端口 或者 地址端口保持默认值,即127.0.0.1:8888
"""
import sys
from typing import Union

from .action import Action
from .exceptions import ContextTypeError
from .model import FriendMsg, GroupMsg
from .utils import file_to_base64


def Text(text: str, at=False):
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
    if 'ctx' in upper_locals and isinstance(upper_locals['ctx'], (FriendMsg, GroupMsg)):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if isinstance(v, (GroupMsg, FriendMsg)):
                ctx = v
                break
    if ctx is None:
        raise ContextTypeError('经支持群消息和好友消息接收函数内调用')

    action = Action(ctx.CurrentQQ)

    if isinstance(ctx, GroupMsg):
        return action.send_group_text_msg(
            ctx.FromGroupId, content=text, atUser=ctx.FromUserId if at else 0
        )
    if isinstance(ctx, FriendMsg):
        if ctx.TempUin:
            return action.send_private_text_msg(
                toUser=ctx.FromUin, content=text, groupid=ctx.TempUin
            )
        else:
            return action.send_friend_text_msg(ctx.FromUin, text)
    return None


def Picture(pic_url='', pic_base64='', pic_path='', content=''):
    """发送图片 经支持群消息和好友消息接收函数内调用
    :param pic_url: 图片链接
    :param pic_base64: 图片base64编码
    :param pic_path: 图片文件路径
    :param content: 包含的文字消息

    pic_url, pic_base64, pic_path必须给定一项
    """
    assert any([pic_url, pic_base64, pic_path]), '必须给定一项'

    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if 'ctx' in upper_locals and isinstance(upper_locals['ctx'], (FriendMsg, GroupMsg)):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if isinstance(v, (FriendMsg, GroupMsg)):
                ctx = v
                break
    if ctx is None:
        raise ContextTypeError('经支持群消息和好友消息接收函数内调用')

    action = Action(ctx.CurrentQQ)

    if isinstance(ctx, GroupMsg):
        if pic_url:
            return action.send_group_pic_msg(
                ctx.FromGroupId, picUrl=pic_url, content=content
            )
        elif pic_base64:
            return action.send_group_pic_msg(
                ctx.FromGroupId, picBase64Buf=pic_base64, content=content
            )
        elif pic_path:
            return action.send_group_pic_msg(
                ctx.FromGroupId, picBase64Buf=file_to_base64(pic_path), content=content
            )
    if isinstance(ctx, FriendMsg):
        if pic_url:
            if ctx.TempUin:
                return action.send_private_pic_msg(
                    toUser=ctx.FromUin,
                    groupid=ctx.TempUin,
                    picUrl=pic_url,
                    content=content,
                )
            else:
                return action.send_friend_pic_msg(
                    ctx.FromUin, picUrl=pic_url, content=content
                )
        elif pic_base64:
            if ctx.TempUin:
                return action.send_private_pic_msg(
                    toUser=ctx.FromUin,
                    groupid=ctx.TempUin,
                    picBase64Buf=pic_base64,
                    content=content,
                )
            else:
                return action.send_friend_pic_msg(
                    ctx.FromUin, picBase64Buf=pic_base64, content=content
                )
        elif pic_path:
            if ctx.TempUin:
                return action.send_private_pic_msg(
                    toUser=ctx.FromUin,
                    groupid=ctx.TempUin,
                    picBase64Buf=file_to_base64(pic_path),
                    content=content,
                )
            else:
                return action.send_friend_pic_msg(
                    ctx.FromUin, picBase64Buf=file_to_base64(pic_path), content=content
                )
    return None


def Voice(voice_url='', voice_base64='', voice_path=''):
    """发送语音 经支持群消息和好友消息接收函数内调用
    :param voice_url: 语音链接
    :param voice_base64: 语音base64编码
    :param voice_path: 语音文件路径

    voice_url, voice_base64, voice_path必须给定一项
    """
    assert any([voice_url, voice_base64, voice_path]), '必须给定一项'

    ctx = None
    f = sys._getframe()
    upper = f.f_back
    upper_locals = upper.f_locals
    if 'ctx' in upper_locals and isinstance(upper_locals['ctx'], (FriendMsg, GroupMsg)):
        ctx = upper_locals['ctx']
    else:
        for v in upper_locals.values():
            if isinstance(v, (GroupMsg, FriendMsg)):
                ctx = v
                break
    if ctx is None:
        raise ContextTypeError('经支持群消息和好友消息接收函数内调用')

    action = Action(ctx.CurrentQQ)

    if isinstance(ctx, GroupMsg):
        if voice_url:
            return action.send_group_voice_msg(ctx.FromGroupId, voiceUrl=voice_url)
        elif voice_base64:
            return action.send_group_voice_msg(
                ctx.FromGroupId, voiceBase64Buf=voice_base64
            )
        elif voice_path:
            return action.send_group_voice_msg(
                ctx.FromGroupId, voiceBase64Buf=file_to_base64(voice_path)
            )
    if isinstance(ctx, FriendMsg):
        if voice_url:
            if ctx.TempUin:
                return action.send_private_voice_msg(
                    toUser=ctx.FromUin, groupid=ctx.TempUin, voiceUrl=voice_url
                )
            else:
                return action.send_friend_voice_msg(ctx.FromUin, voiceUrl=voice_url)
        elif voice_base64:
            if ctx.TempUin:
                return action.send_private_voice_msg(
                    toUser=ctx.FromUin, groupid=ctx.TempUin, voiceBase64Buf=voice_base64
                )
            else:
                return action.send_friend_voice_msg(
                    ctx.FromUin, voiceBase64Buf=voice_base64
                )
        elif voice_path:
            if ctx.TempUin:
                return action.send_private_voice_msg(
                    toUser=ctx.FromUin,
                    groupid=ctx.TempUin,
                    voiceBase64Buf=file_to_base64(voice_path),
                )
            else:
                return action.send_friend_voice_msg(
                    ctx.FromUin, voiceBase64Buf=file_to_base64(voice_path)
                )
    return None


def Send(
    ctx: Union[FriendMsg, GroupMsg],
    *,
    text: str = '',
    pic_url: str = '',
    pic_base64: str = '',
    pic_path: str = '',
    voice_url: str = '',
    voice_base64: str = '',
    voice_path: str = ''
):
    """
    根据给定参数自动选择发送方式, 支持对群聊、好友(包括私聊)
    所有参数均为可选参数
    图片和语音支持的三种参数类型，分别三选一，如果传入多个则优先级为: url > base64 > path
    """
    assert isinstance(ctx, (FriendMsg, GroupMsg))
    if text:
        Text(text)
    if any((pic_url, pic_base64, pic_path)):
        Picture(pic_url, pic_base64, pic_path)
    if any((voice_url, voice_base64, voice_path)):
        Voice(voice_url, voice_base64, voice_path)
