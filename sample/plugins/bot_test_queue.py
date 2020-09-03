from iotbot import Action, GroupMsg
from iotbot.decorators import equal_content, not_botself

action = Action(123456, queue=True, queue_delay=2)  # 唯一写法


@not_botself
@equal_content('queue')
def receive_group_msg(ctx: GroupMsg):
    action.send_group_text_msg(ctx.FromGroupId, '这条消息每次发送间隔不会低于2秒。。。', callback=print)
