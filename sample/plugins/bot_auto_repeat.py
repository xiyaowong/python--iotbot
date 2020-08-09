import os
from queue import deque

from iotbot import GroupMsg
from iotbot.decorators import not_botself
from iotbot.decorators import only_these_groups
from iotbot.sugar import Text

# 连续多少条相同信息时+1
big_mouth_len = int(os.getenv('big_mouth_len') or 4)
big_mouth_deque = deque(maxlen=big_mouth_len)
for i in range(big_mouth_len):
    big_mouth_deque.append(i)


@not_botself
@only_these_groups([11111111111])
def receive_group_msg(ctx: GroupMsg):
    content = ctx.Content
    if len(content) < 30:
        big_mouth_deque.append(content)
        if len(set(big_mouth_deque)) == 1:
            Text(content)
            for i in range(big_mouth_len):
                big_mouth_deque.append(i)
