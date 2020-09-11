# 防撤回插件
import json
import os
from pathlib import Path

# pip install pymongo
import pymongo
from iotbot import Action, EventMsg, GroupMsg
from iotbot import decorators as deco
from iotbot.refine_message import refine_group_revoke_event_msg
from iotbot.sugar import Text
from iotbot.utils import MsgTypes

# TODO: 对不同的群做不同的开关逻辑

client = pymongo.MongoClient()  # TODO 自行修改配置
db = client.iotbot.revoke

FLAG = Path(__file__).absolute().parent / 'STOPREVOKEFLAG'  # 功能开关标记文件
# 在哪些群开启
whiteList = [1, 222]
# 哪些人可以控制开关, 发送“开关防撤回”切换插件开启状态
admins = [
    333,
    4444,
    55555,
    666666,
]


@deco.not_botself
@deco.only_these_groups(whiteList)
def receive_group_msg(ctx: GroupMsg):
    if ctx.Content == '开关防撤回' and ctx.FromUserId in admins:
        if FLAG.exists():  # 存在说明开启状态，则关闭。
            os.remove(FLAG)
        else:
            FLAG.touch()
        Text('ok')

    # 储存消息
    if ctx.MsgType in [MsgTypes.TextMsg, MsgTypes.PicMsg, MsgTypes.AtMsg]:
        db.insert_one(
            {
                'msg_type': ctx.MsgType,
                'msg_random': ctx.MsgRandom,
                'msg_seq': ctx.MsgSeq,
                'msg_time': ctx.MsgTime,
                'user_id': ctx.FromUserId,
                'user_name': ctx.FromNickName,
                'group_id': ctx.FromGroupId,
                'content': ctx.Content,
            }
        )


def receive_events(ctx: EventMsg):
    if not FLAG.exists():  # 功能关闭状态
        return

    revoke_ctx = refine_group_revoke_event_msg(ctx)
    if revoke_ctx is None:  # 只处理撤回事件
        return

    bot = revoke_ctx.CurrentQQ
    user_id = revoke_ctx.UserID
    if user_id == bot:  # 不接受自己的消息
        return

    admin = revoke_ctx.AdminUserID
    group_id = revoke_ctx.FromUin
    msg_random = revoke_ctx.MsgRandom
    msg_seq = revoke_ctx.MsgSeq

    found = db.find_one(
        {
            'msg_random': msg_random,
            'msg_seq': msg_seq,
            'user_id': user_id,
            'group_id': group_id,
        }
    )

    if found:
        msg_type = found['msg_type']
        user_id = found['user_id']
        user_name = found['user_name']
        group_id = found['group_id']
        content = found['content']

        if admin != found['user_id']:  # 不相等說明是管理員撤回
            return

        if msg_type == MsgTypes.TextMsg:
            Action(bot).send_group_text_msg(
                found['group_id'], f'[{user_id}{user_name}]撤回了: \n{content}'
            )
        elif msg_type == MsgTypes.PicMsg:
            pic_data = json.loads(content)
            Action(bot).send_group_pic_msg(
                group_id,
                fileMd5=pic_data['GroupPic'][0]['FileMd5'],
                content='[{}{}]撤回了：\n[PICFLAG]{}'.format(
                    user_id, user_name, pic_data.get('Content') or ''
                ),
            )
        elif msg_type == MsgTypes.AtMsg:
            at_data = json.loads(found['content'])
            at_content = at_data['Content']
            Action(bot).send_group_text_msg(
                group_id,
                content='[{who}{user_name} 刚刚撤回了艾特{at_user}]\n{content}'.format(
                    who=user_id,
                    user_name=user_name,
                    at_user='&'.join((str(i) for i in at_data['UserID'])),
                    content=at_content[at_content.rindex(' ') + 1 :],
                ),
            )
