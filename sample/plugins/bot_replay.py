# 增强版复读机
from time import sleep

from iotbot import GroupMsg
from iotbot.decorators import in_content, not_botself
from iotbot.refine import refine_pic_group_msg
from iotbot.sugar import Picture, Text
from iotbot.utils import MsgTypes


@not_botself
@in_content('复读机')
def receive_group_msg(ctx: GroupMsg):
    if ctx.MsgType == MsgTypes.TextMsg:
        if not ctx.Content.startswith('复读机'):
            return
        text = ctx.Content[3:]  # type: str
        while '复读机' in text:  # 防止别人搞鬼发这种东西: 复读机复复读机读复读机机
            text = text.replace('复读机', '')
        if text:
            Text(text)
    elif ctx.MsgType == MsgTypes.PicMsg:
        pic_ctx = refine_pic_group_msg(ctx)
        if pic_ctx is None:
            return
        for pic in pic_ctx.GroupPic:
            Picture(pic_url=pic.Url)
            sleep(1)
    elif ctx.MsgType == MsgTypes.AtMsg:
        # TODO
        pass
