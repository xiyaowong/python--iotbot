import os
import random
import re

from iotbot import Action, GroupMsg


def receive_group_msg(ctx: GroupMsg):
    if ctx.FromUserId == ctx.CurrentQQ:
        return

    content = ctx.Content  # type:str

    # 妹子图
    if re.findall(r"(妹子|小姐姐|美女)", content):
        random.seed(os.urandom(100))
        Action(ctx.CurrentQQ).send_group_pic_msg(
            ctx.FromGroupId,
            picUrl=random.choice([  # 随便找的api
                'http://api.btstu.cn/sjbz/?lx=meizi',
                'http://api.btstu.cn/sjbz/?lx=m_meizi',
                'http://api.btstu.cn/sjbz/?m_lx=suiji',
            ])
        )
        return
