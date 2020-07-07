# https://github.com/yuban10703/IOTQQ-color_pic
# 仅做示例
import re

import requests

from iotbot import GroupMsg
from iotbot.decorators import in_content
from iotbot.sugar import Picture, Text

pattern = r'来(.*?)[点丶份张幅](.*?)的?[色瑟涩][图圖]'
api = 'http://api.yuban10703.xyz:2333/setu_v3'


@in_content('[色瑟涩][图圖]')
def receive_group_msg(ctx: GroupMsg):
    if ctx.FromUserId == ctx.CurrentQQ:
        return

    tag = re.findall(pattern, ctx.Content)
    tag = tag[0][1] if tag else ''
    try:
        r = requests.get(api, params={'tag': tag, 'num': 1}, timeout=10)
    except Exception:
        Text('老子出毛病了，稍后再试~')
    else:
        info = r.json()
        if info['count'] == 0:
            Text('没有没有，不要问了，没有!')
        else:
            Picture('https://cdn.jsdelivr.net/gh/laosepi/setu/pics_original/'
                    + info['data'][0]['filename'])
