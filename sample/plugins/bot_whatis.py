import requests
from iotbot import GroupMsg
from iotbot.decorators import not_botself, only_this_msg_type
from iotbot.sugar import Text
from iotbot.utils import MsgTypes

# 查网络缩写词的意思
# ?nmsl => 查nmsl
# ?awsl => 查awsl


def whatis(text):
    if not (1 < len(text) < 10):
        return ''
    try:
        resp = requests.post(
            'https://lab.magiconch.com/api/nbnhhsh/guess',
            data={'text': text},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(e)
        return ''
    else:
        if not data:
            return ''
        name, trans = data[0]['name'], data[0]['trans']
        trans_str = '、'.join(trans)
        return f'【{name}】{trans_str}'


@not_botself
@only_this_msg_type(MsgTypes.TextMsg)
def receive_group_msg(ctx: GroupMsg):
    if ctx.Content.startswith('?'):
        text = ctx.Content[1:]
        ret = whatis(text)
        if ret:
            Text(ret)
