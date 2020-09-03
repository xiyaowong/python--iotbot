import requests

from iotbot import Action, GroupMsg
from iotbot.decorators import equal_content, not_botself

# 推荐用lua写


@not_botself
@equal_content('网易云热评')
def receive_group_msg(ctx: GroupMsg):
    try:
        rep = requests.get('https://www.mouse123.cn/api/163/api.php', timeout=10)
        rep.raise_for_status()
        data = rep.json()
        Action(ctx.CurrentQQ).send_group_pic_msg(
            ctx.FromGroupId,
            content='歌曲: {title}\n歌手: {author}\n评论: {comment}'.format(
                title=data['title'],
                author=data['author'],
                comment=data['comment_content'],
            ),
            picUrl=data['images'],
        )
    except Exception:
        pass
