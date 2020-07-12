import requests

from iotbot import Action
from iotbot import GroupMsg
from iotbot.decorators import equal_content
from iotbot.decorators import not_botself
from iotbot.sugar import Text

# 推荐用lua写


@not_botself
@equal_content('诗句')
def receive_group_msg(ctx: GroupMsg):
    try:
        rep = requests.get('https://v1.jinrishici.com/all.json', timeout=10)
        rep.raise_for_status()
        content: str = rep.json()['content']
        origin: str = rep.json()['origin']
        author: str = rep.json()['author']
        temp = [origin, f'【{author}】', content]
        max_len = max([len(x) for x in temp])
        Text('\n'.join([x.center(max_len) for x in temp]))
    except Exception as e:
        print(e)
