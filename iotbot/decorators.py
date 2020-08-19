import functools
import re

from .model import FriendMsg
from .model import GroupMsg


def in_content(string: str):
    """
    接受消息content字段含有指定消息时, 不支持事件类型消息
    :param string: 支持正则
    """
    def deco(func):
        def inner(ctx):
            if isinstance(ctx, (GroupMsg, FriendMsg)):
                if re.findall(string, ctx.Content):
                    return func(ctx)
            return None
        return inner
    return deco


def equal_content(string: str):
    """
    content字段与指定消息相等时, 不支持事件类型消息
    """
    def deco(func):
        def inner(ctx):
            if isinstance(ctx, (GroupMsg, FriendMsg)):
                if ctx.Content == string:
                    return func(ctx)
            return None
        return inner
    return deco


def not_botself(func=None):
    """忽略机器人自身的消息"""
    if func is None:
        return functools.partial(not_botself)

    def inner(ctx):
        if isinstance(ctx, (GroupMsg, FriendMsg)):
            if isinstance(ctx, GroupMsg):
                userid = ctx.FromUserId
            else:
                userid = ctx.FromUin
            if userid != ctx.CurrentQQ:
                return func(ctx)
        return None
    return inner


def is_botself(func=None):
    """只要机器人自身的消息"""
    if func is None:
        return functools.partial(not_botself)

    def inner(ctx):
        if isinstance(ctx, (GroupMsg, FriendMsg)):
            if isinstance(ctx, GroupMsg):
                userid = ctx.FromUserId
            else:
                userid = ctx.FromUin
            if userid == ctx.CurrentQQ:
                return func(ctx)
        return None
    return inner


def not_these_users(users: list):
    """不接受这些人的消息
    :param users: qq号列表
    """
    def deco(func):
        def inner(ctx):
            nonlocal users
            if isinstance(ctx, (GroupMsg, FriendMsg)):
                if not hasattr(users, '__iter__'):
                    users = [users]
                if isinstance(ctx, GroupMsg):
                    from_user = ctx.FromUserId
                elif isinstance(ctx, FriendMsg):
                    from_user = ctx.FromUin
                if from_user not in users:
                    return func(ctx)
            return None
        return inner
    return deco


def only_these_users(users: list):
    """仅接受这些人的消息
    :param users: qq号列表
    """
    def deco(func):
        def inner(ctx):
            nonlocal users
            if isinstance(ctx, (GroupMsg, FriendMsg)):
                if not hasattr(users, '__iter__'):
                    users = [users]
                if isinstance(ctx, GroupMsg):
                    from_user = ctx.FromUserId
                elif isinstance(ctx, FriendMsg):
                    from_user = ctx.FromUin
                if from_user in users:
                    return func(ctx)
            return None
        return inner
    return deco


def only_this_msg_type(msg_type: str):
    """仅接受该类型消息
    :param msg_type: TextMsg, PicMsg, AtMsg, ReplyMsg, VoiceMsg之一
    """
    def deco(func):
        def inner(ctx):
            if isinstance(ctx, (GroupMsg, FriendMsg)):
                if ctx.MsgType == msg_type:
                    return func(ctx)
            return None
        return inner
    return deco


def not_these_groups(groups: list):
    """不接受这些群组的消息
    :param groups: 群号列表
    """
    def deco(func):
        def inner(ctx):
            nonlocal groups
            if isinstance(ctx, GroupMsg):
                if not hasattr(groups, '__iter__'):
                    groups = [groups]
                if isinstance(ctx, GroupMsg):
                    from_group = ctx.FromGroupId
                    if from_group not in groups:
                        return func(ctx)
            return None
        return inner
    return deco


def only_these_groups(groups: list):
    """只接受这些群组的消息
    :param groups: 群号列表
    """
    def deco(func):
        def inner(ctx):
            nonlocal groups
            if isinstance(ctx, GroupMsg):
                if not hasattr(groups, '__iter__'):
                    groups = [groups]
                if isinstance(ctx, GroupMsg):
                    from_group = ctx.FromGroupId
                    if from_group in groups:
                        return func(ctx)
            return None
        return inner
    return deco
