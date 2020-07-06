"""
封装部分最常用发送操作
"""

import base64
from typing import Union

from .action import Action
from .model import FriendMsg, GroupMsg


def Text(ctx: Union[GroupMsg, FriendMsg],
         text: str,
         at=False):
    """发送文字
    :param ctx:
    :param text: 文字内容
    :param at:是否艾特发送该消息的用户
    """
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
    ##################################################
    else:
        raise BaseException('参数ctx必须为GroupMsg或Friendmsg')


def Picture(ctx: Union[GroupMsg, FriendMsg],
            pic_url='',
            pic_base64='',
            pic_path=''):
    """发送图片
    :param ctx:
    :param pic_url: 图片链接
    :param pic_base64: 图片base64编码
    :param pic_path: 图片文件路径

    pic_url, pic_base64, pic_path必须给定一项
    """
    assert any([pic_url, pic_base64, pic_path])
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
            b64 = base64.b64decode(content)
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
            b64 = base64.b64decode(content)
            return Action(ctx.CurrentQQ).send_friend_pic_msg(
                ctx.FromUin,
                picBase64Buf=b64
            )
        return None
    else:
        raise BaseException('参数ctx必须为GroupMsg或Friendmsg')
