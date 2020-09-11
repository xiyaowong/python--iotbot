import os
import random
import re
import time

from iotbot import Action, GroupMsg
from iotbot.decorators import in_content, is_botself

# 机器人自己发送的消息中包含关键字 revoke 就自动撤回
# 仅包含关键字 随机30s-80s后撤回
# revoke[10] => 10s后撤回
# revoke[20] => 20s后撤回


@is_botself
@in_content('revoke')
def receive_group_msg(ctx: GroupMsg):
    delay = re.findall(r'revoke\[(\d+)\]', ctx.Content)
    if delay:
        delay = min(int(delay[0]), 90)
    else:
        random.seed(os.urandom(30))
        delay = random.randint(30, 80)
    time.sleep(delay)

    Action(ctx.CurrentQQ).revoke_msg(
        groupid=ctx.FromGroupId, msgseq=ctx.MsgSeq, msgrandom=ctx.MsgRandom
    )
