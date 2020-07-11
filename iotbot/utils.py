from enum import Enum


class MsgType(Enum):
    """消息类型"""
    AtMsg = 'AtMsg'
    PicMsg = 'PicMsg'
    TextMsg = 'TextMsg'
    ReplyMsg = 'ReplyMsg'
    VoiceMsg = 'VoiceMsg'
