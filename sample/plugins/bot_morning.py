from datetime import datetime

from iotbot.decorators import equal_content
from iotbot.sugar import Text


def get_msg():
    now_ = datetime.now()
    hour = now_.hour
    minute = now_.minute
    now = hour + minute / 60

    if 5.5 < now < 8:
        msg = '早~'
    elif 8 <= now < 18:
        msg = '这个点还早啥，昨晚干啥去了？'
    elif 18 <= now < 21:
        msg = '尼玛，老子准备洗洗睡了'
    else:
        msg = '你是夜猫子？'
    return msg


@equal_content('早')
def receive_group_msg(_):
    Text(get_msg())


@equal_content('早')
def receive_friend_msg(_):
    Text(get_msg())
