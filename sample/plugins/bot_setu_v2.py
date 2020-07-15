# https://github.com/yuban10703/IOTQQ-color_pic
import os
import re

import requests
from iotbot import Action
from iotbot import GroupMsg
from iotbot import decorators as deco
from iotbot.sugar import Text

pattern = r'来(.*?)[点丶份张幅](.*?)的?[色瑟涩][图圖]'
api = 'http://api.yuban10703.xyz:2333/setu_v3'

action = Action(
    int(os.getenv('BOTQQ') or 123456),
    queue=True
)


@deco.not_botself
@deco.in_content(pattern)
def receive_group_msg(ctx: GroupMsg):
    num = 1
    tag = ''

    info = re.findall(pattern, ctx.Content)
    if info:
        num = int(info[0][0] or 1)
        tag = info[0][1]
    if num > 5:
        Text('服了，要那么多干嘛，我只发5张！')
        num = 5

    try:
        r = requests.get(api, params={'tag': tag, 'num': num}, timeout=10)
    except Exception:
        Text('老子出毛病了，稍后再试~')
    else:
        info = r.json()
        if info['count'] == 0:
            Text('没有没有，不要问了，没有!')
        else:
            for i in info['data']:
                action.send_group_pic_msg(
                    ctx.FromGroupId,
                    picUrl='https://cdn.jsdelivr.net/gh/laosepi/setu/pics_original/' + i['filename'],
                    content=f"标题:{i['title']}\n作者: {i['author']}"
                )
