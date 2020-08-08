# 该功能即是一个内置插件
import traceback

import requests

from . import sugar
from .config import config
from .exceptions import InvalidConfigError
from .model import EventMsg
from .model import FriendMsg
from .model import GroupMsg


def _check_config():
    if not config.webhook_post_url:
        raise InvalidConfigError('缺少配置项: webhook_post_url')


_check_config()


def receive_group_msg(ctx: GroupMsg):
    try:
        resp = requests.post(config.webhook_post_url,
                             json=ctx.message,
                             timeout=config.webhook_timeout)
        resp.raise_for_status()
    except Exception:
        print(traceback.format_exc())
    else:
        try:
            data = resp.json()
            assert isinstance(data, dict)
        except Exception:
            pass
        else:
            # 取出所有支持的字段
            # 1. 图片(pic)存在，发送图片消息，此时文字(msg)存在, 则发送图文消息
            # 2. 图片(pic)不存在, 文字(msg)存在，单独发送文字消息
            # 3. 语音(voice)只要存在，则发送
            msg: str = data.get('msg') or ''
            at: bool = bool(data.get('at')) or False  # 只要存在值就判定真
            pic_url: str = data.get('pic_url')
            pic_base64: str = data.get('pic_base64')
            voice_url: str = data.get('voice_url')
            voice_base64: str = data.get('voice_base64')
            if any([pic_url, pic_base64]):  # 图片，纯文字二选一
                sugar.Picture(pic_url=pic_url, pic_base64=pic_base64, content=msg)
            elif msg:
                sugar.Text(msg, at)
            if any([voice_url, voice_base64]):
                sugar.Voice(voice_url=voice_url, voice_base64=voice_base64)
            return None
    return None


def receive_friend_msg(ctx: FriendMsg):
    try:
        resp = requests.post(config.webhook_post_url,
                             json=ctx.message,
                             timeout=config.webhook_timeout)
        resp.raise_for_status()
    except Exception:
        print(traceback.format_exc())
    else:
        try:
            data = resp.json()
            assert isinstance(data, dict)
        except Exception:
            pass
        else:
            # 取出所有支持的字段
            # 1. 图片(pic)存在，发送图片消息，此时文字(msg)存在, 则发送图文消息
            # 2. 图片(pic)不存在, 文字(msg)存在，单独发送文字消息
            # 3. 语音(voice)只要存在，则发送
            msg: str = data.get('msg') or ''
            at: bool = bool(data.get('at')) or False  # 只要存在值就判定真
            pic_url: str = data.get('pic_url')
            pic_base64: str = data.get('pic_base64')
            voice_url: str = data.get('voice_url')
            voice_base64: str = data.get('voice_base64')
            if any([pic_url, pic_base64]):  # 图片，纯文字二选一
                sugar.Picture(pic_url=pic_url, pic_base64=pic_base64, content=msg)
            elif msg:
                sugar.Text(msg, at)
            if any([voice_url, voice_base64]):
                sugar.Voice(voice_url=voice_url, voice_base64=voice_base64)
            return None
    return None


def receive_events(ctx: EventMsg):
    # 事件消息只上报(懒)
    try:
        requests.post(config.webhook_post_url,
                      json=ctx.message,
                      timeout=config.webhook_timeout)
    except Exception:
        pass
