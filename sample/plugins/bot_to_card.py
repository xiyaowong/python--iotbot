# 可用于调试卡片消息
import json

from iotbot import Action
from iotbot import GroupMsg
from iotbot.decorators import in_content


@in_content('转卡片')
def receive_group_msg(ctx: GroupMsg):
    content = ctx.Content.replace('转卡片', '').strip()
    action = Action(ctx.CurrentQQ)
    try:
        json_text = json.dumps(json.loads(content))
        action.send_group_json_msg(ctx.FromGroupId, content=json_text)
    except Exception:
        action.send_group_xml_msg(ctx.FromGroupId, content=content)
